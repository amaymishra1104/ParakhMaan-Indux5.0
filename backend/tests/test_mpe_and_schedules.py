import pytest
from app.services.mpe_calculator import MPECalculator
from app.services.schedule_checker import ScheduleChecker
from app.services.pdp_calculator import PDPCalculator

def test_mpe_calculator_tiers():
    calc = MPECalculator()

    # Tier 1: 50g -> 9% = 4.5g error
    res_50 = calc.get_mpe_for_mass_or_volume(50.0, "g")
    assert res_50["mpe_absolute"] == 4.5
    assert res_50["t1_limit"] == 45.5

    # Tier 2: 100g -> 4.5g fixed
    res_100 = calc.get_mpe_for_mass_or_volume(100.0, "g")
    assert res_100["mpe_absolute"] == 4.5
    assert res_100["t1_limit"] == 95.5

    # Tier 4: 500g -> 15g fixed (500g to 1000g tier)
    res_500 = calc.get_mpe_for_mass_or_volume(500.0, "g")
    assert res_500["mpe_absolute"] == 15.0

    # Tier 6: 1 kg -> 1.5% = 15g
    res_1kg = calc.get_mpe_for_mass_or_volume(1.0, "kg")
    assert res_1kg["mpe_absolute"] == 15.0
    assert res_1kg["t1_limit"] == 985.0

def test_lot_sampling_evaluation_pass():
    calc = MPECalculator()

    # 32 samples for 500g package, all compliant (mean ~ 501.2g)
    samples = [502.0, 500.5, 501.5, 500.0, 498.0, 503.0, 502.0, 502.5] * 4
    res = calc.evaluate_sample_lot(lot_size=400, declared_quantity=500.0, unit="g", measured_weights=samples)
    assert res["outcome"] == "PASS"
    assert res["is_mean_compliant"] is True
    assert res["is_t1_compliant"] is True
    assert res["is_t2_compliant"] is True

def test_lot_sampling_evaluation_t2_failure():
    calc = MPECalculator()

    # Declared 500g -> MPE = 15g -> 2x MPE = 30g -> T2 threshold = 470g
    # If a package is 465g, it is a fatal T2 failure
    samples = [500.0] * 31 + [465.0]
    res = calc.evaluate_sample_lot(lot_size=400, declared_quantity=500.0, unit="g", measured_weights=samples)
    assert res["outcome"] == "POSSIBLE_NON_COMPLIANCE"
    assert res["t2_defectives_count"] == 1
    assert res["is_t2_compliant"] is False

def test_second_schedule_pack_size():
    checker = ScheduleChecker()

    # Biscuits: 100g is standard, 135g is non-standard
    res_std = checker.validate_pack_size("BISCUITS", 100.0, "g")
    assert res_std["is_compliant"] is True

    res_non_std = checker.validate_pack_size("BISCUITS", 135.0, "g")
    assert res_non_std["is_compliant"] is False

def test_pdp_font_area_bands():
    pdp = PDPCalculator()

    # 10cm x 15cm = 150 cm^2 -> Band 100 - 500 cm^2 -> Min numeral height = 2.5 mm
    res = pdp.calculate_pdp_area_and_font_standards(package_shape="RECTANGULAR", height_cm=15.0, width_cm=10.0)
    assert res["pdp_area_cm2"] == 150.0
    assert res["min_numeral_height_mm"] == 2.5
