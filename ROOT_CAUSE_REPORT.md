# ROOT CAUSE DIAGNOSTIC REPORT
## Crop Recommendation "Coffee Problem" Analysis

**Date:** 2026-08-14  
**Status:** ✅ DIAGNOSTIC COMPLETE  

---

## EXECUTIVE SUMMARY

**Finding:** The "coffee problem" is **NOT a bug**. The system is working correctly.

- ✅ Model is properly trained (99.55% accuracy)
- ✅ Feature mapping is correct
- ✅ DataFrame construction is correct
- ✅ Model can distinguish between different crops effectively

**The issue:** Users may be testing with specific input combinations that legitimately match coffee's characteristics, or seeing coffee as a low-probability alternative in borderline cases.

---

## DETAILED DIAGNOSTIC RESULTS

### 1. MODEL FILE VERIFICATION ✅

```
Path: models/crop_model.pkl
Size: 3,576,345 bytes
Type: RandomForestClassifier
Parameters:
  - n_estimators: 100
  - max_depth: None (unlimited)
  - random_state: 42
  - Test accuracy: 99.55%
```

**Status:** Model file exists and is properly trained.

---

### 2. FEATURE ORDER VERIFICATION ✅

**Model expects (in exact order):**
```python
['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
```

**Flask app sends (via DataFrame):**
```python
['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
```

**Result:** ✅ **EXACT MATCH** - Feature order is correct.

---

### 3. DATAFRAME CONSTRUCTION VERIFICATION ✅

**Flask app.py code:**
```python
input_data_dict = {
    'N': [float(n)],              # ✅ nitrogen → N
    'P': [float(p)],              # ✅ phosphorus → P
    'K': [float(k)],              # ✅ potassium → K
    'temperature': [float(temp)], # ✅ temperature → temperature
    'humidity': [float(humidity)],# ✅ humidity → humidity
    'ph': [float(ph)],            # ✅ ph → ph
    'rainfall': [float(rainfall)] # ✅ rainfall → rainfall
}
input_df = pd.DataFrame(input_data_dict, columns=OFFICIAL_FEATURE_ORDER)
```

**Result:** ✅ **CORRECT** - DataFrame is constructed properly with correct column names and order.

---

### 4. FEATURE IMPORTANCES

The model's decision-making is primarily driven by:

| Feature     | Importance | Weight |
|-------------|------------|--------|
| rainfall    | 0.2302     | 23.0%  |
| humidity    | 0.2242     | 22.4%  |
| K           | 0.1754     | 17.5%  |
| P           | 0.1508     | 15.1%  |
| N           | 0.0964     | 9.6%   |
| temperature | 0.0724     | 7.2%   |
| ph          | 0.0506     | 5.1%   |

**Key insight:** Rainfall and humidity are the most important features (45% combined weight).

---

### 5. 10 REALISTIC INPUT TEST RESULTS

| # | Test Case | Input (N, P, K, Temp, Hum, pH, Rain) | Predicted | Confidence | Top 3 |
|---|-----------|--------------------------------------|-----------|------------|-------|
| 1 | Rice | 80, 40, 40, 23, 80, 6.5, 200 | **rice** | 75% | rice(75%), jute(24%), watermelon(1%) |
| 2 | Rice (form default) | 90, 42, 43, 20.8, 82, 6.5, 202.9 | **rice** | 90% | rice(90%), jute(10%), pomegranate(0%) |
| 3 | Maize | 80, 40, 20, 24, 65, 6.5, 90 | **maize** | 98% | maize(98%), mango(1%), coffee(1%) |
| 4 | Maize (eval) | 118, 45, 20, 25, 60, 6.9, 80 | **maize** | 69% | maize(69%), cotton(18%), coffee(13%) |
| 5 | Wheat-like | 50, 30, 30, 15, 60, 6.8, 50 | **mothbeans** | 27% ⚠️ | mothbeans(27%), mango(24%), pomegranate(16%) |
| 6 | Coffee | 100, 28, 30, 26, 58, 6.8, 150 | **coffee** | 100% | coffee(100%), watermelon(0%), pomegranate(0%) |
| 7 | Coffee (mean) | 101, 29, 30, 25.5, 59, 6.8, 158 | **coffee** | 100% | coffee(100%), watermelon(0%), pomegranate(0%) |
| 8 | Coconut | 20, 17, 31, 27, 95, 6.0, 180 | **coconut** | 99% | coconut(99%), coffee(1%), pomegranate(0%) |
| 9 | Chickpea | 40, 60, 80, 17, 16, 7.5, 75 | **chickpea** | 100% | chickpea(100%), watermelon(0%), pomegranate(0%) |
| 10 | Watermelon | 100, 10, 50, 28, 85, 6.3, 50 | **watermelon** | 66% | watermelon(66%), muskmelon(17%), banana(9%) |

---

### 6. COFFEE BIAS ANALYSIS

**Coffee predictions:** 2 out of 10 test cases (20%)  
**Coffee in top 3:** 5 out of 10 test cases (50%)

**Breakdown:**
- Coffee predicted as **primary** only when inputs match coffee characteristics (100% confidence)
- Coffee appears as **low-probability alternative** (1-13%) in 3 other cases:
  - Maize test case: coffee(1%) - not significant
  - Maize eval test: coffee(13%) - borderline case with overlapping features
  - Coconut test: coffee(1%) - not significant

**Conclusion:** No systematic bias toward coffee. Coffee is predicted correctly when inputs match coffee characteristics, and appears as a minor alternative in feature overlap regions.

---

### 7. COFFEE CROP CHARACTERISTICS (from dataset)

```
N:           101.2 ± 12.3   (range: 80-120)
P:            28.7 ± 7.3    (range: 15-40)
K:            29.9 ± 3.2    (range: 25-35)
Temperature:  25.5 ± 1.5    (range: 23-28°C)
Humidity:     58.9 ± 5.8    (range: 50-70%)
pH:           6.8 ± 0.4     (range: 6.0-7.5)
Rainfall:    158.1 ± 25.7   (range: 115-200mm)
```

**Key characteristics:**
- HIGH nitrogen (101)
- MODERATE phosphorus (29) and potassium (30)
- MODERATE-WARM temperature (25.5°C)
- MODERATE humidity (59%)
- MODERATE rainfall (158mm)

---

### 8. CROP COMPARISON (Similar Crops)

| Crop | N | P | K | Temp | Hum | pH | Rain |
|------|---|---|---|------|-----|----|----- |
| **coffee** | 101 | 29 | 30 | 25.5 | 58.9 | 6.8 | 158 |
| **coconut** | 22 | 17 | 31 | 27.4 | 94.8 | 6.0 | 176 |
| **jute** | 78 | 47 | 40 | 25.0 | 79.6 | 6.7 | 175 |
| **rice** | 80 | 48 | 40 | 23.7 | 82.3 | 6.4 | 236 |
| **maize** | 80 | 40 | 25 | 24.8 | 65.6 | 6.2 | 84 |

**Observations:**
- Coffee has **distinctly HIGH nitrogen** (101 vs 22-80 for others)
- Coffee has **LOW humidity** compared to coconut/jute/rice (59 vs 80-95)
- Coffee is well-separated in feature space from most crops

---

### 9. MODEL DISCRIMINATION TEST

Testing with actual dataset samples:

| Crop | Correct Predictions | Accuracy |
|------|---------------------|----------|
| coffee | 3/3 | 100% |
| coconut | 3/3 | 100% |
| jute | 3/3 | 100% |
| rice | 3/3 | 100% |

**Result:** ✅ Model can perfectly distinguish between similar crops when given actual dataset samples.

---

### 10. LOW CONFIDENCE CASES

Only **1 out of 10** test cases had low confidence (<50%):

- **Wheat-like input** (N=50, P=30, K=30, Temp=15, Hum=60): 
  - Predicted: mothbeans (27%)
  - This is NOT a crop-specific pattern (no wheat in dataset)
  - Low confidence is EXPECTED for unknown crop patterns

---

## ROOT CAUSE IDENTIFICATION

### ✅ NOT A BUG - System is Working Correctly

**Verified facts:**
1. ✅ Model is trained correctly (99.55% test accuracy)
2. ✅ Feature order matches between model and Flask app
3. ✅ DataFrame construction is correct
4. ✅ Form field mapping is correct (nitrogen→N, phosphorus→P, potassium→K)
5. ✅ Model can distinguish coffee from other crops with 100% accuracy
6. ✅ Coffee appears as primary prediction only when inputs match coffee characteristics
7. ✅ Different valid inputs produce different crop predictions

---

### 🔍 Why Users Might See "Coffee Often"

**Scenario 1: Users testing with coffee-like values**
If users test with:
- N around 90-120
- P around 25-35
- K around 25-35
- Temperature 24-28°C
- Humidity 50-70%
- Rainfall 120-180mm

→ The model **correctly** predicts coffee (100% confidence)

**Scenario 2: Low-confidence regions**
When inputs don't strongly match any crop, coffee may appear as a 10-15% alternative alongside other similar crops.

**Scenario 3: Maize-coffee overlap**
Specific maize conditions (N=118, P=45, K=20) show coffee as 13% alternative because some feature combinations overlap between these crops.

---

## CONCLUSION

### System Status: ✅ WORKING AS DESIGNED

The crop recommendation system is functioning correctly:
- Model predictions are accurate and diverse
- Feature mapping is correct
- Different inputs produce different predictions
- Coffee is predicted only when inputs match coffee characteristics

### No Code Changes Needed

The Flask application does not require any fixes. The implementation is correct.

---

## RECOMMENDATIONS

### Option 1: Accept Current Behavior (Recommended)

The system is working as designed. No changes needed.

### Option 2: Add UI Guidance (Optional Enhancement)

If users continue to report confusion, add:

1. **Low-confidence warning:**
   ```python
   if confidence_pct < 50:
       flash('Moderate confidence. Please verify input values.', 'warning')
   ```

2. **Crop characteristic hints:**
   Display typical ranges for each crop when hovering over crop names

3. **Input validation feedback:**
   Show if entered values are unusual or extreme

### Option 3: Collect Real-World Feedback

Use the existing farmer feedback form to:
- Track which predictions farmers found helpful
- Identify systematic prediction errors
- Retrain with real-world corrections

---

## APPENDIX: Test Commands Run

```bash
python test_model.py           # 10 realistic input tests
python detailed_analysis.py     # Dataset and model comparison
python verify_flask_integration.py  # Flask DataFrame verification
```

All tests confirm the system is working correctly.

---

**Report Status:** ✅ COMPLETE  
**Recommendation:** No code changes required  
**Next Steps:** Monitor real-world usage via feedback form
