
https://consumeraffairs.gov.in/pages/legal-metrology-overview?utm_source=chatgpt.com


https://consumeraffairs.gov.in/pages/weight-and-measures?utm_source=chatgpt.com

https://consumeraffairs.gov.in/pages/latest-news?utm_source=chatgpt.com


Yes. If by **“every single rule”** you mean the complete rule structure that your SIH26034 engine needs to know, we need to go substantially deeper than the earlier 40-rule abstraction.

I checked the underlying **Legal Metrology (Packaged Commodities) Rules, 2011** and the Government's current Legal Metrology repository. The Rules contain **Rules 1–34, 7 Schedules, and numerous sub-rules/provisos**, with amendments from 2011 through 2026. The Department's official page confirms the amendment history through the **Third Amendment Rules, 2026**. ([Consumer Affairs][1])

Below is the complete **rule-by-rule map**. This is a structured explanation, not a replacement for the Gazette text.

---

# SIH26034 — COMPLETE LEGAL METROLOGY RULE MAP

## CHAPTER I — PRELIMINARY

### Rule 1 — Short title and commencement

Defines the name:

**Legal Metrology (Packaged Commodities) Rules, 2011**

The original Rules came into force on **1 April 2011**. ([India Code][2])

**AI relevance:** LOW

---

# Rule 2 — Definitions

This is extremely important for your engine because applicability depends on these definitions.

Important defined concepts include:

* Act
* Consumer
* Dealer
* Industrial consumer
* Institutional consumer
* E-commerce
* E-commerce entity
* Marketplace-based e-commerce
* Manufacturer
* Maximum permissible error
* Net quantity
* Packer
* Principal Display Panel
* Quantity
* Retail dealer
* Retail package
* Retail sale
* Retail sale price
* Schedule
* Standard package
* Wholesale dealer
* Wholesale package

For example, **net quantity excludes the packaging/wrapper**, and a wholesale package includes specified groupings of retail packages. ([India Code][2])

**AI relevance:** VERY HIGH

Your classifier should derive:

```text
retail_package
wholesale_package
industrial_consumer
institutional_consumer
imported_package
ecommerce
```

before applying subsequent rules.

---

# CHAPTER II — PACKAGES INTENDED FOR RETAIL SALE

## Rule 3 — Application of Chapter

The retail-package chapter does **not automatically apply to everything**.

The current rule structure excludes:

* packages containing more than **25 kg / 25 litre**
* cement, fertilizer and agricultural farm produce sold in bags above **50 kg**
* packages meant for industrial consumers
* packages meant for institutional consumers

subject to the exact current provisions and amendments. ([India Code][2])

### AI check

```text
Is this package within Chapter II scope?
```

This should happen **before** running the normal retail checklist.

---

# Rule 4 — Regulation for pre-packing and sale

A commodity intended for sale/distribution/delivery cannot be pre-packed unless the package or securely attached label contains the declarations required by the Rules.

There is a specific treatment for packages inside the manufacturer's premises that do not yet have the retail sale price; packages leaving the premises must carry the required declaration. ([India Code][2])

### AI checks

* Is it a pre-packaged commodity?
* Are required declarations present?
* Is MRP present before the package leaves the relevant premises?

---

# Rule 5 — Standard packages

Commodities listed in the **Second Schedule** must be packed in the specified standard quantities.

There are provisions for:

* standard pack quantities
* promotional/group packages
* value-based packages

The Second Schedule therefore becomes an important **commodity → permitted pack-size lookup table**. ([India Code][2])

### AI engine

```text
commodity
+
declared quantity
↓
Second Schedule lookup
↓
permitted?
```

---

# Rule 6 — Declarations on every package

🔥 **This is the single most important rule for your project.**

Every applicable package must carry definite, plain and conspicuous declarations.

The rule covers:

### 6(a) Manufacturer / packer / importer

Identify:

* manufacturer
* packer, where different
* importer for imported packages

There are additional rules concerning brand-owner/marketer responsibility and food products, where other food legislation applies to specified matters. ([India Code][2])

### 6(aa) Country of origin

For imported products:

```text
country of origin / manufacture / assembly
```

must be declared as applicable. ([India Code][2])

### 6(b) Common/generic name

The package must identify the commodity.

For packages containing multiple products, the names and number/quantity of each product are relevant. ([India Code][2])

### 6(c) Net quantity

The package must declare the net quantity using the applicable standard unit of:

* mass
* measure
* number

as applicable. ([India Code][2])

### 6(d) Manufacturing / packing / importing date information

The month and year requirements apply subject to specified exceptions and sector-specific laws.

Examples of special treatment include:

* food
* seeds
* cosmetics
* bidi
* incense sticks
* specified LPG cylinders

([India Code][2])

### 6(da) Best-before / use-by

Where the commodity may become unfit for human consumption after a period, the applicable best-before/use-by information must be declared, subject to other applicable laws. ([India Code][2])

### 6(e) Retail Sale Price

The package must declare the retail sale price/MRP in the prescribed form, including the tax treatment required by the rule.

Special provisions exist for:

* alcoholic beverages
* essential commodities with notified prices
* certain excluded packages

([India Code][2])

### 6(f) Dimensions

Where relevant, dimensions of the commodity must be declared.

Where pieces have different dimensions, the relevant individual dimensions must also be declared. ([India Code][2])

### 6(g) Other required information

The rule incorporates other matters required elsewhere in the Rules.

---

### Rule 6 also contains additional requirements concerning:

* consumer-care contact information
* restrictions on altering mandatory declarations with stickers
* permitted lower-MRP stickers
* optional barcode/GTIN/QR code information
* multi-component packages
* leftover packaging material
* genetically modified food marking
* vegetarian/non-vegetarian marking for specified cosmetics/toiletries
* labels on imported packages
* e-commerce display of mandatory declarations

The e-commerce provisions also contain marketplace-intermediary responsibilities and do **not** remove the requirement for declarations on the physical package delivered to consumers. ([India Code][2])

### This should become your main AI extraction schema

```text
manufacturer
packer
importer
country_of_origin
generic_name
product_name
net_quantity
manufacture_or_pack_date
best_before
use_by
mrp
dimensions
consumer_care
special_declarations
```

---

# Rule 7 — Principal Display Panel: area, size and letters

This is your **font-size / visual compliance rule**.

For very small packages, a card/tape can serve as the principal display panel subject to the rule.

The current rule specifies minimum height requirements for numerals and letters based on the **area of the principal display panel**, and also requires minimum letter/numeral width relative to height. ([India Code][2])

The current table includes area bands:

```text
≤ 50 cm²
>50 – ≤100 cm²
>100 – ≤500 cm²
>500 – ≤2500 cm²
>2500 cm²
```

with corresponding minimum character heights.

The rule also specifies how the principal display panel area is determined for:

* rectangular packages
* cylindrical/nearly cylindrical packages
* other shapes

([India Code][2])

### THIS IS YOUR FONT-SIZE AI MODULE

```text
image
↓
PDP detection
↓
PDP area estimation
↓
text bounding box
↓
character-height measurement
↓
minimum-height lookup
↓
PASS / REVIEW
```

---

# Rule 8 — Where declarations must appear

Required declarations must appear on the **principal display panel**.

The area around the quantity declaration must be free from printed information with prescribed spacing:

* above/below
* left/right

There is a specific provision for returnable bottles used for soft drinks/ready-to-serve fruit beverages and similar products concerning MRP placement. ([India Code][2])

### AI checks

```text
PDP detected?
quantity inside required area?
clear space?
MRP location?
```

---

# Rule 9 — Manner of declaration

Declarations must be:

* legible
* prominent
* suitably contrasting where required

MRP and net quantity numerals have specific contrast requirements.

There are exceptions for certain molded/formed/blown information.

Declarations cannot require the consumer to read through the contained liquid.

Outer wrappers/containers generally need the required declarations unless the applicable transparency exception applies.

Declarations must be in:

* Hindi in Devanagari, or
* English

Additional languages are allowed. ([India Code][2])

### AI modules

```text
OCR readability
contrast analysis
language detection
PDP placement
outer-wrapper analysis
```

---

# Rule 10 — Manufacturer / packer / importer name and address

Packages must display the applicable manufacturer/packer/importer name and complete address.

There are special provisions for:

* very small packages
* products manufactured outside India but packed in India
* what constitutes a complete address
* actual corporate/business name

([India Code][2])

### AI

```text
ENTITY_NAME
ADDRESS
ROLE
COUNTRY
```

---

# Rule 11 — General provisions for quantity

This rule controls **how net quantity is determined and declared**.

Packaging material is excluded.

For commodities whose quantity does not materially vary due to environmental conditions:

```text
declared quantity
≈
quantity consumer receives
```

For commodities affected by environmental conditions, the rules distinguish between:

* negligible variation
* significant variation

Certain commodities can therefore use the **“when packed”** qualification according to the Third Schedule. ([India Code][2])

---

# Rule 12 — Manner of declaring quantity

The quantity must be expressed using appropriate weight/measure/number.

Normally:

### Solid / semi-solid / viscous

→ mass

### Linear commodity

→ length

### Area commodity

→ area

### Liquid

→ volume

### Commodity sold by number

→ number

But the **Fourth Schedule contains exceptions**. ([India Code][2])

The rule also prohibits misleading quantity expressions. The 2011 amendment specifically strengthened this principle. ([India Code][3])

---

# Rule 13 — Units

This is another important machine-readable rule.

For quantities below the relevant larger unit:

* kilogram → gram
* metre → centimetre
* square metre → square decimetre
* litre → millilitre
* etc.

For larger quantities, the corresponding larger standard unit is used, subject to the permitted representations. ([India Code][2])

The rule also says:

* don't use "dozen", "score", "gross", "great gross" etc. as the quantity declaration
* use SI units
* packages sold by number use the prescribed number symbols
* multiple identical packages require supplementary quantity information

([India Code][2])

### AI

This should be a deterministic **unit-normalization engine**, not an LLM.

---

# Rule 14 — Dimensions of certain commodities

Applies to products such as:

* bed sheets
* fabric
* dhotis
* sarees
* napkins
* pillow covers
* towels
* table cloths
* similar commodities

Requires:

* number of pieces
* finished dimensions

For differently sized pieces, dimensions and applicable price information must be provided. ([India Code][2])

---

# Rule 15 — Dimensions/weight related to price

If the price depends on:

* dimensions
* weight
* combination of dimensions and weight

the package must declare those relevant quantities. ([India Code][2])

---

# Rule 16 — Number of usable sheets

For packages containing sheets such as:

* aluminium foil
* facial tissues
* waxed paper
* toilet paper
* similar sheets

the declaration includes:

* number of usable sheets
* dimensions of each sheet

([India Code][2])

---

# Rule 17 — Container-type commodities

For products such as:

* bags
* boxes
* cups
* pans
* similar containers

the declaration depends on the shape/type.

Examples include:

```text
bags
→ number + linear dimensions

rectangular containers
→ number + length + width + depth where required

round containers
→ number + diameter + depth where required
```

Label references to capacity/standard size can also be relevant. ([India Code][2])

---

# Rule 18 — Wholesale/retail dealer requirements

A wholesale dealer, retail dealer or importer cannot sell/store/display packaged commodities that don't comply with the Act and Rules.

The rule also addresses:

* direct sale to industrial/institutional consumers
* selling above MRP
* multiple MRP practices
* tax-driven revised prices
* restrictions on changing/obliterating MRP
* retail weighing-machine requirements
* LPG cylinder check-weight requirements

([India Code][2])

### AI relevance

Mostly **inspection/enforcement intelligence**, rather than package OCR.

---

# Rule 19 — Inspection at manufacturer/packer premises

This is the beginning of the **actual enforcement inspection procedure**.

An authorized Legal Metrology officer can:

* inspect packages
* draw samples
* test net quantity
* use Fifth Schedule sampling
* use Sixth Schedule testing methodology
* record results
* report findings

([India Code][2])

Failure conditions include:

* corrected average below declared quantity
* excessive number of deficient packages
* any package exceeding twice the maximum permissible error
* declaration violations

Depending on the result, the manufacturer/packer may be required to perform a **100% check**, re-pack/re-label, etc. ([India Code][2])

This is extremely relevant to your proposed **lot intelligence** module.

---

# Rule 20 — Action after inspection at manufacturer/packer

Where inspection reveals quantity/declaration violations, the officer can:

* seize representative packages
* preserve evidence
* initiate action under the Act/Rules

The rules also govern release/compliance treatment. ([India Code][2])

---

# Rule 21 — Inspection at wholesale/retail premises

Testing at retailer/wholesaler premises is generally not the ordinary first step, except where circumstances justify it, such as:

* consumer complaint
* suspected tampering
* suspected pilferage/leakage
* suspected missing declarations

The officer verifies:

```text
actual quantity
vs
declared quantity
```

and compares deficiency against the Maximum Permissible Error.

([India Code][2])

---

# Rule 22 — Establishment of Maximum Permissible Error

Maximum permissible error is governed by the **First Schedule**.

The rule takes into account:

* unavoidable weighing/measuring/counting variation
* normal climate/transport/storage variation
* packaging/container effects
* environmental variation for “when packed” commodities

([India Code][2])

This is crucial because:

> **Declared quantity ≠ exact physical measurement requirement**

There is a legally defined tolerance.

---

# Rule 23 — Deceptive packages

A package may be treated as deceptive where its design deliberately gives an exaggerated or misleading impression regarding quantity.

However, larger packaging may be justified where necessary for:

* protecting the commodity
* accommodating filling machinery

([India Code][2])

### This is a fantastic AI feature.

Your computer vision could calculate:

```text
package_volume
vs
approximate_product_volume
```

and flag:

> **Potentially deceptive package — REVIEW**

Never automatically declare it illegal.

---

# CHAPTER III — WHOLESALE PACKAGES

# Rule 24 — Wholesale package declarations

A wholesale package must carry clear declarations concerning:

1. manufacturer/importer/packer identity
2. identity of commodity
3. total number of retail packages OR net quantity in standard units

There is an exception where another applicable law already requires equivalent declarations. ([India Code][2])

---

# CHAPTER IV — EXPORT PACKAGES

# Rule 25 — Export packages sold in India

An export package cannot simply be sold domestically as-is.

Before sale in India it must be:

```text
repacked
OR
relabeled
```

to comply with the applicable domestic packaged-commodity provisions.

Non-compliant export packages may be seized. ([India Code][2])

---

# CHAPTER V — EXEMPTIONS

# Rule 26 — Exemptions

The rule provides exemptions for specified package situations.

The underlying rule includes, among other things:

* very small quantities
* certain restaurant/hotel fast-food packages
* specified drug formulations
* specified thread sold in coils to handloom weavers

and contains specific qualifications concerning tobacco/tobacco products and medical devices. ([India Code][2])

**This is why your AI must have:**

```text
NOT_APPLICABLE
EXEMPTED
```

rather than only PASS/FAIL.

---

# CHAPTER VI — REGISTRATION

# Rule 27 — Registration of manufacturers, packers and importers

Persons/entities manufacturing, packing or importing commodities for sale/distribution/delivery are subject to registration requirements.

The rule specifies:

* application
* registration
* fee
* applicant identity
* premises address
* commodities
* registration certificate

([India Code][2])

The **2026 Third Amendment** introduces additional registration-related provisions, including annual updating and director responsibility/validity provisions. The current Government repository lists that amendment. ([Consumer Affairs][1])

---

# Rule 28 — Registration of shorter address

A manufacturer/packer can apply to register a shorter address.

The authority can approve it if the shorter address is sufficient to identify the manufacturer/packer.

Once registered, that shorter address may be used on package labels. ([India Code][2])

---

# Rule 29 — Registration records

The Director/Controller maintains a register containing registered manufacturer/packer information.

The register is open to public inspection without payment of a fee. ([India Code][2])

---

# Rule 30 — State-wise manufacturer/packer lists

The Director/Controller compiles State-wise lists of registered manufacturers/packers and circulates them to the relevant Controller for enforcement/sampling. ([India Code][2])

---

# CHAPTER VII — GENERAL

# Rule 31 — Advertisements

If an advertisement mentions the retail sale price of a pre-packaged commodity, it must also state:

```text
net quantity OR number
```

The font size of the quantity/number declaration in the advertisement must be the same as the retail sale price. ([India Code][2])

### AI extension

Your system could eventually inspect:

```text
Amazon/Flipkart/website advertisement
MRP
quantity
font-size relationship
```

---

# Rule 32 — Fine for contravention

Where no specific punishment is provided for a contravention of the Rules, Rule 32 provides the applicable fine.

The rule has been amended over time, so **do not hard-code historical penalty values without checking the current Act/Rules**. ([India Code][2])

---

# Rule 32A — Compounding

Provides the compounding framework/table for specified offences under the Act.

The amounts depend on the offence and the class of applicant, including retailer/wholesale dealer versus manufacturer/importer. ([India Code][2])

This belongs in your **enforcement module**, not the image classifier.

---

# Rule 33 — Power to relax

The Central Government can, after considering the genuineness of a case, permit specified manufacturers/packers/importers to operate under relaxed requirements for a specified period and conditions.

It also provides a mechanism concerning packages outside the Second Schedule. ([India Code][2])

### AI

Your engine should support:

```text
RULE_RELAXATION = TRUE
approval/reference = ...
valid_until = ...
```

rather than blindly flagging the package.

---

# Rule 34 — Repeal and savings

The 1977 Standards of Weights and Measures (Packaged Commodities) Rules were repealed.

However, prior:

* actions
* rights
* obligations
* liabilities
* penalties
* investigations
* proceedings
* remedies

are preserved according to the savings provisions. ([India Code][2])

**AI relevance:** essentially none for package inspection.

---

# NOW THE SCHEDULES

This is where our earlier database was **not complete enough**.

## FIRST SCHEDULE — Maximum Permissible Error

Contains permissible errors for:

### Weight / volume

Different declared-quantity bands have different permissible errors.

### Length

For commodities not otherwise specified, the rule provides percentage-based tolerance.

### Area

Separate percentage-based tolerance.

### Number

Separate percentage-based tolerance.

The Schedule is directly tied to Rules 19–22. ([India Code][2])

**Your backend absolutely needs this as a numerical lookup table.**

---

# SECOND SCHEDULE — Standard Pack Quantities

This is a **major dataset**.

It contains commodity-specific standard pack sizes.

Examples in the Schedule include categories such as:

* tea
* weaning food
* bread
* butter/margarine
* cereals/pulses
* coffee
* salt
* soaps
* detergents
* beverages
* paints
* etc.

The actual permitted quantities must be stored **commodity by commodity**, not summarized as “food has standard sizes.” ([India Code][2])

### Your database needs:

```text
commodity_id
commodity_name
minimum_quantity
maximum_quantity
permitted_sizes[]
unit
effective_date
source
```

---

# THIRD SCHEDULE — “When Packed”

Identifies commodities for which quantity declarations can be qualified with **“when packed”**.

The Schedule includes commodities such as:

* soaps
* lotions
* cream other than milk cream
* camphor

([India Code][2])

---

# FOURTH SCHEDULE — Exceptions to normal quantity units

This is extremely important for your category classifier.

Examples include:

| Commodity                            | Permitted quantity basis   |
| ------------------------------------ | -------------------------- |
| Aerosol products                     | Weight                     |
| Liquid acids                         | Weight or volume           |
| Compressed/liquefied gas             | Weight + equivalent volume |
| Curd                                 | Weight                     |
| Electric cables                      | Length or weight           |
| Electric wire                        | Length or weight           |
| Fencing wire                         | Number or weight           |
| Fruits                               | Number or weight           |
| Furnace oil                          | Weight or volume           |
| Non-edible vegetable oil             | Weight or volume           |
| Edible oil/vanaspati/ghee/butter oil | Weight or volume           |
| LPG                                  | Weight                     |
| Nails/wood screws                    | Number or weight           |
| Paints                               | Volume                     |
| Paste/solid paint                    | Weight                     |
| Rasgulla/Gulabjamun                  | Weight                     |
| Ready-made garments                  | Number                     |
| Sauces                               | Weight                     |
| Tyres/tubes                          | Number                     |
| Yarn                                 | Weight or length           |
| Cosmetics                            | Weight or measure          |

([India Code][2])

**This is exactly why your system needs a commodity-specific rules layer.**

---

# FIFTH SCHEDULE — Sampling

Used for Rule 19 inspection.

The Schedule specifies sample-selection methodology based on lot size.

The underlying schedule provides sample-size rules and requires random selection. It also specifies representative selection across warehouse stock positions such as:

```text
top
bottom
centre
right
left
front
rear
```

([India Code][2])

This maps beautifully to your planned **lot/warehouse intelligence**.

---

# SIXTH SCHEDULE — Determination of net quantity

Contains the official procedure for determining net quantity.

It covers:

### Equipment

* working-standard weights
* balances
* appropriate measures
* other suitable equipment

### Verification

Equipment must be functioning properly.

### Working standards

Verified working standards are ordinarily used.

### Manufacturer-owned equipment

Specified conditions apply when the officer uses equipment belonging to the manufacturer/packer/wholesaler.

([India Code][2])

The remainder of the Schedule contains the actual measurement methodologies.

---

# SEVENTH SCHEDULE — Inspection/test reporting

The Rules also provide the prescribed form/data structure for recording inspection/testing results under Rule 19.

This is particularly relevant to your **digital inspection report**.

Your system should ultimately reproduce something like:

```text
Inspection ID
Officer
Date
Premises
Product
Lot
Declared quantity
Measured quantity
Permissible error
Observed error
Declarations
Violations
Evidence
Action
```

---

# BUT THERE IS ANOTHER CRITICAL LAYER

The above is the **base 2011 Rules + their internal structure**.

It is **not yet the final 2026 legal state**.

The Department's official repository lists amendments in:

* 2011
* 2012
* 2013
* 2014
* 2015
* 2016
* 2017
* 2021
* 2022
* 2023
* 2025
* 2026

plus corrigenda, implementation guidelines, advisories and SOPs. ([Consumer Affairs][1])

And some amendments materially change the engine.

For example, the 2026 amendments include the e-commerce country-of-origin requirement timeline, while the April 2026 amendment changed the commencement date to **1 July 2027**. So a rule engine cannot simply say:

```text
Rule 6(10A) = active
```

It needs:

```text
rule_id
version
effective_from
effective_until
status
```

---

# The correct database architecture

For your SIH project, I now recommend **five rule layers**:

```text
                    LEGAL METROLOGY ENGINE
                            │
             ┌──────────────┴──────────────┐
             │                             │
       APPLICABILITY                  EFFECTIVE DATE
             │                             │
             └──────────────┬──────────────┘
                            ↓
                    BASE RULES 1–34
                            ↓
                    SCHEDULES 1–7
                            ↓
              AMENDMENTS / CORRIGENDA
                            ↓
               CATEGORY-SPECIFIC MATERIAL
                            ↓
                    EXEMPTIONS
                            ↓
                   VALIDATION ENGINE
                            ↓
             PASS / REVIEW / POSSIBLE NC
```

And your product-specific rule selection should look like:

```text
PRODUCT
│
├── Is it pre-packaged?
│
├── Retail / wholesale?
│
├── Industrial / institutional?
│
├── Domestic / imported?
│
├── Food?
│
├── Cosmetic?
│
├── Medical device?
│
├── Agricultural produce?
│
├── Edible oil/fat?
│
├── Pan masala?
│
├── E-commerce?
│
├── Quantity type?
│   ├── Mass
│   ├── Volume
│   ├── Length
│   ├── Area
│   └── Number
│
├── Standard-pack commodity?
│
├── Exemption?
│
└── Special amendment?
```

Then:

```text
Applicable rules
       ↓
OCR / CV evidence
       ↓
Deterministic validation
       ↓
Evidence-backed verdict
```

## One correction to our previous deliverable

**The earlier `SIH26034_RULE_DATABASE_v1` I gave you should NOT be treated as the final “every rule” database.**

It was an implementation-oriented starter rule set. After going through the actual structure, I would upgrade it substantially to include:

1. **All Rules 1–34**
2. **Every relevant sub-rule**
3. **First Schedule numerical MPE tables**
4. **Complete Second Schedule commodity/pack-size table**
5. **Third Schedule**
6. **Fourth Schedule commodity/unit table**
7. **Fifth Schedule sampling tables**
8. **Sixth Schedule measurement procedures**
9. **Seventh Schedule inspection/report structure**
10. **Every amendment affecting current applicability**
11. **2025/2026 effective dates**
12. **Exemptions**
13. **Category-specific Government advisories/SOPs**
14. **Source document + notification number for every rule**
15. **`ACTIVE / SUPERSEDED / FUTURE / REPEALED` status**

That is what I would consider a genuinely serious **SIH26034 legal-rule knowledge base**.

The Government's own Legal Metrology repository is the authoritative starting point, while India Code provides the underlying Rules and notifications; India Code itself cautions that the Department's/Gazette's document remains the authority. ([Consumer Affairs][1])

**If your goal is to put this directly into the project, the next deliverable should therefore be a v2 database containing the complete Rules + all seven Schedules + amendment/version mapping, rather than simply adding more generic checklist rows.**

[1]: https://consumeraffairs.gov.in/index.php/pages/legal-metrology-act?utm_source=chatgpt.com "The Legal Metrology Act"
[2]: https://indiacode.ecourtsindia.com/rules/b62ed6c1/ "Legal Metrology (Packaged Commodities) Rule, 2011 (2011) | IndiaCode"
[3]: https://upload.indiacode.nic.in/showfile?actid=AC_PB_82_942_00004_00004_1550217305600&filename=the_legal_metrology_%28packaged_commodities%29_rules%2C2011_with_amendments.pdf&type=rule&utm_source=chatgpt.com "!EJ 
\~tio ito ~o-33004/99 
REGD. NO. D. L.-33004/9"