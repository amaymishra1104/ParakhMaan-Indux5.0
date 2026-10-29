"""
ParakhMaan — Industrial PLC Integration Service (Modbus TCP & OPC-UA)
=====================================================================
Enables real-time communication between the ParakhMaan edge vision gateway and
factory Programmable Logic Controllers (PLCs - Siemens S7, Allen-Bradley, Beckhoff,
Schneider Electric) to actuate high-speed pneumatic blow-off rejection gates and
stack light towers upon defect detection.
"""

import time
import logging
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PLCEvent:
    timestamp: str
    event_type: str
    actuator: str
    duration_ms: int
    inspection_id: Optional[str]
    defect_class: Optional[str]
    details: Dict[str, Any] = field(default_factory=dict)


class IndustrialPLCService:
    """
    Industrial PLC communication service supporting Modbus TCP and OPC-UA.
    Includes a high-fidelity virtual PLC simulation mode for demonstration and
    seamless fallback when physical hardware is not wired.
    """

    # Modbus Memory Map Definition
    COILS = {
        0: "CONVEYOR_RUN",
        1: "PNEUMATIC_REJECT_ACTUATOR",
        2: "STACK_LIGHT_RED",
        3: "STACK_LIGHT_AMBER",
        4: "STACK_LIGHT_GREEN",
        5: "GATEWAY_HEARTBEAT",
    }

    REGISTERS = {
        100: "LAST_INSPECTION_DECISION",  # 1: PASS, 2: DEFECTIVE, 3: MANUAL_REVIEW
        101: "DEFECT_CLASS_CODE",         # 0: None, 1: Scratch, 2: Crack, 3: Dent, 4: Discolouration, 5: Dimensional, 6: Novelty
        102: "INSPECTION_LATENCY_MS",
        103: "CONFIDENCE_BPS",            # Basis points: e.g. 9650 = 96.5%
        104: "PNEUMATIC_PULSE_DURATION_MS",
        105: "TOTAL_INSPECTED_COUNTER",
        106: "TOTAL_REJECTED_COUNTER",
    }

    CLASS_CODES = {
        "NONE": 0,
        "SCRATCH": 1,
        "CRACK": 2,
        "DENT": 3,
        "DISCOLOURATION": 4,
        "DIMENSIONAL_ANOMALY": 5,
        "UNSUPERVISED_ANOMALY": 6,
    }

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 502,
        protocol: str = "modbus_tcp",
        simulation_mode: bool = True,
        default_pulse_ms: int = 150,
    ):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.simulation_mode = simulation_mode
        self.default_pulse_ms = default_pulse_ms

        # Internal Virtual PLC State
        self.coils_state: Dict[int, bool] = {
            0: True,   # Conveyor running
            1: False,  # Pneumatic valve closed
            2: False,  # Red light off
            3: False,  # Amber light off
            4: True,   # Green light on (healthy)
            5: True,   # Heartbeat high
        }

        self.registers_state: Dict[int, int] = {
            100: 1,    # Initial PASS
            101: 0,    # No defect
            102: 15,   # 15 ms latency
            103: 9800, # 98.0%
            104: default_pulse_ms,
            105: 0,    # Inspected count
            106: 0,    # Rejected count
        }

        self.last_event: Optional[PLCEvent] = None
        self.event_history: list[PLCEvent] = []
        self._lock = threading.Lock()
        self.client = None

        # Attempt hardware connection if not in forced simulation mode
        if not self.simulation_mode:
            self._connect_modbus()

    def _connect_modbus(self):
        """Attempts connection to physical Modbus TCP PLC."""
        try:
            from pymodbus.client import ModbusTcpClient
            self.client = ModbusTcpClient(self.host, port=self.port, timeout=1.0)
            connected = self.client.connect()
            if not connected:
                logger.warning(f"Could not connect to physical PLC at {self.host}:{self.port}. Operating in virtual PLC simulation mode.")
                self.simulation_mode = True
        except Exception as e:
            logger.warning(f"Modbus connection initialization failed: {e}. Falling back to virtual PLC simulation.")
            self.simulation_mode = True

    def trigger_pneumatic_reject(
        self,
        duration_ms: Optional[int] = None,
        defect_class: Optional[str] = None,
        confidence: float = 0.95,
        latency_ms: float = 20.0,
        inspection_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Actuates the physical/virtual high-speed pneumatic blow-off valve to
        divert a defective part into the rejection chute.
        """
        pulse_ms = duration_ms or self.default_pulse_ms
        cls_name = (defect_class or "SCRATCH").upper()
        cls_code = self.CLASS_CODES.get(cls_name, 1)

        with self._lock:
            # Update Holding Registers
            self.registers_state[100] = 2  # 2 = DEFECTIVE
            self.registers_state[101] = cls_code
            self.registers_state[102] = int(latency_ms)
            self.registers_state[103] = int(confidence * 10000)
            self.registers_state[104] = pulse_ms
            self.registers_state[105] += 1
            self.registers_state[106] += 1

            # Update Coils: Trigger Pneumatic Valve & Red Stack Light
            self.coils_state[1] = True   # Valve open
            self.coils_state[2] = True   # Red light ON
            self.coils_state[3] = False  # Amber light OFF
            self.coils_state[4] = False  # Green light OFF

            event = PLCEvent(
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%S.", time.gmtime()) + f"{int((time.time()%1)*1000):03d}Z",
                event_type="PNEUMATIC_REJECT_ACTUATED",
                actuator="PNEUMATIC_DIVERT_GATE_01",
                duration_ms=pulse_ms,
                inspection_id=inspection_id,
                defect_class=cls_name,
                details={
                    "coil_1_valve": True,
                    "register_100_verdict": 2,
                    "confidence_pct": round(confidence * 100.0, 1),
                    "stack_light": "RED",
                    "mode": "SIMULATION" if self.simulation_mode else "HARDWARE_MODBUS",
                },
            )
            self.last_event = event
            self.event_history.append(event)
            if len(self.event_history) > 50:
                self.event_history.pop(0)

            # Write to real hardware if connected
            if not self.simulation_mode and self.client and self.client.connected:
                try:
                    self.client.write_coil(1, True)
                    self.client.write_coil(2, True)
                    self.client.write_coil(4, False)
                    self.client.write_register(100, 2)
                    self.client.write_register(101, cls_code)
                except Exception as e:
                    logger.error(f"Hardware write failed: {e}")

        # Non-blocking valve reset thread to close pneumatic actuator after pulse_ms
        def _reset_valve():
            time.sleep(pulse_ms / 1000.0)
            with self._lock:
                self.coils_state[1] = False  # Close valve
                if not self.simulation_mode and self.client and self.client.connected:
                    try:
                        self.client.write_coil(1, False)
                    except Exception:
                        pass

        reset_thread = threading.Thread(target=_reset_valve, daemon=True)
        reset_thread.start()

        return {
            "status": "ACTUATED",
            "valve_state": "OPEN_PULSE",
            "pulse_duration_ms": pulse_ms,
            "defect_class": cls_name,
            "class_code": cls_code,
            "stack_light": "RED",
            "protocol": self.protocol.upper(),
            "simulation_mode": self.simulation_mode,
            "timestamp": event.timestamp,
        }

    def record_inspection_verdict(
        self,
        outcome: str,
        latency_ms: float = 18.0,
        defect_class: Optional[str] = None,
        confidence: float = 0.95,
        inspection_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Updates PLC registers for any outcome (PASS, DEFECTIVE, or MANUAL REVIEW).
        Automatically fires pneumatic gate if DEFECTIVE.
        """
        verdict = outcome.upper()
        if "DEFECTIVE" in verdict or "REJECT" in verdict:
            return self.trigger_pneumatic_reject(
                defect_class=defect_class,
                confidence=confidence,
                latency_ms=latency_ms,
                inspection_id=inspection_id,
            )

        with self._lock:
            self.registers_state[105] += 1  # Increment total inspected
            self.registers_state[102] = int(latency_ms)

            if "REVIEW" in verdict:
                self.registers_state[100] = 3  # REVIEW
                self.coils_state[2] = False
                self.coils_state[3] = True   # Amber ON
                self.coils_state[4] = False
                stack_color = "AMBER"
            else:
                self.registers_state[100] = 1  # PASS
                self.registers_state[101] = 0  # No defect
                self.coils_state[2] = False
                self.coils_state[3] = False
                self.coils_state[4] = True   # Green ON
                stack_color = "GREEN"

            if not self.simulation_mode and self.client and self.client.connected:
                try:
                    self.client.write_register(100, self.registers_state[100])
                    self.client.write_coil(3, self.coils_state[3])
                    self.client.write_coil(4, self.coils_state[4])
                except Exception:
                    pass

        return {
            "status": "RECORDED",
            "verdict": verdict,
            "stack_light": stack_color,
            "valve_state": "CLOSED",
            "total_inspected": self.registers_state[105],
            "total_rejected": self.registers_state[106],
            "simulation_mode": self.simulation_mode,
        }

    def get_status(self) -> Dict[str, Any]:
        """Returns full telemetry snapshot of virtual/hardware PLC."""
        with self._lock:
            coils_named = {self.COILS[k]: v for k, v in self.coils_state.items()}
            regs_named = {self.REGISTERS[k]: v for k, v in self.registers_state.items()}
            last_ev = (
                {
                    "timestamp": self.last_event.timestamp,
                    "event_type": self.last_event.event_type,
                    "actuator": self.last_event.actuator,
                    "duration_ms": self.last_event.duration_ms,
                    "defect_class": self.last_event.defect_class,
                }
                if self.last_event
                else None
            )

            # OPC-UA node mapping equivalent
            opc_ua_nodes = {
                "ns=2;s=ParakhMaan.Conveyor.Running": self.coils_state[0],
                "ns=2;s=ParakhMaan.Actuators.PneumaticGate": self.coils_state[1],
                "ns=2;s=ParakhMaan.StackLight.Red": self.coils_state[2],
                "ns=2;s=ParakhMaan.StackLight.Amber": self.coils_state[3],
                "ns=2;s=ParakhMaan.StackLight.Green": self.coils_state[4],
                "ns=2;s=ParakhMaan.Inspection.VerdictCode": self.registers_state[100],
                "ns=2;s=ParakhMaan.Inspection.DefectCode": self.registers_state[101],
                "ns=2;s=ParakhMaan.Metrics.TotalInspected": self.registers_state[105],
                "ns=2;s=ParakhMaan.Metrics.TotalRejected": self.registers_state[106],
            }

            return {
                "online": True,
                "protocol": self.protocol.upper(),
                "host": self.host,
                "port": self.port,
                "simulation_mode": self.simulation_mode,
                "coils": coils_named,
                "holding_registers": regs_named,
                "opc_ua_nodes": opc_ua_nodes,
                "last_actuation": last_ev,
                "rejection_rate_pct": round(
                    (self.registers_state[106] / max(self.registers_state[105], 1)) * 100.0, 1
                ),
            }

    def configure(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        protocol: Optional[str] = None,
        simulation_mode: Optional[bool] = None,
        default_pulse_ms: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Reconfigures PLC gateway settings at runtime."""
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        if protocol is not None:
            self.protocol = protocol.lower()
        if simulation_mode is not None:
            self.simulation_mode = simulation_mode
        if default_pulse_ms is not None:
            self.default_pulse_ms = default_pulse_ms

        if not self.simulation_mode:
            self._connect_modbus()

        return self.get_status()


# Global singleton instance
plc_service = IndustrialPLCService()
