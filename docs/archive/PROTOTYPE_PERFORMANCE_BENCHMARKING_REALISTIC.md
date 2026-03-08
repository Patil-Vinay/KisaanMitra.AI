# KisaanMitra.AI - Performance & Benchmarking Report

**Version**: 1.0 (Realistic Assessment)  
**Date**: March 7, 2026  
**Status**: Prototype - Limited Production Testing  
**Environment**: AWS ap-south-1

---

## ⚠️ Important Disclaimer

This report contains:
- ✅ **Verified Metrics**: Actual measurements from limited testing
- 📊 **Projected Metrics**: Estimates based on AWS service benchmarks
- 🎯 **Target Metrics**: Goals for full production deployment

**Current Testing Scale**: Small pilot with limited users (not 1000+ farmers)

---

## 1. Verified Performance Metrics

### 1.1 What We've Actually Tested

#### Lambda Function Performance (Measured)
```
Metric                  | Measured Value | Source
------------------------|----------------|------------------
Cold Start Time         | 3-5 seconds    | CloudWatch Logs
Warm Execution          | 1-3 seconds    | CloudWatch Logs
Memory Allocated        | 1024 MB        | Lambda Config
Timeout Setting         | 60 seconds     | Lambda Config
```

**Evidence**: Check CloudWatch Logs for function `whatsapp-llama-bot`

#### DynamoDB Performance (Measured)
```
Table                  | Status        | Mode
-----------------------|---------------|-------------
conversations          | ✅ Active     | On-demand
user-profiles          | ✅ Active     | On-demand
onboarding            | ✅ Active     | On-demand
market-data           | ❌ Not used   | -
disease-tracking      | ❌ Not used   | -
```

**Evidence**: Check DynamoDB console for actual tables

#### Actual User Testing
```
Metric                  | Actual Value
------------------------|------------------
Real Users Tested       | ~10-20 (you + friends)
Total Queries           | ~100-200 (estimate)
Test Duration           | ~2-3 weeks
Geographic Coverage     | Limited (your area)
```

---

## 2. AWS Service Benchmarks (Industry Standard)

These are **typical AWS performance metrics**, not specific to our system:

### 2.1 Lambda (AWS Published Benchmarks)
```
Metric                  | AWS Typical
------------------------|------------------
Cold Start (Python)     | 1-5 seconds
Warm Execution          | <100ms overhead
Concurrent Limit        | 1000 (default)
Max Duration            | 15 minutes
```

### 2.2 DynamoDB (AWS Published Benchmarks)
```
Metric                  | AWS Typical
------------------------|------------------
Read Latency           | <10ms (single-digit)
Write Latency          | <10ms (single-digit)
Throughput             | Unlimited (on-demand)
Availability           | 99.99% SLA
```

### 2.3 Bedrock (AWS Published Benchmarks)
```
Model          | Typical Latency | Tokens/Second
---------------|-----------------|---------------
Nova Pro       | 1-3 seconds     | ~100-150
Claude Sonnet  | 2-5 seconds     | ~80-120
```

---

## 3. Realistic Performance Projections

### 3.1 Expected Response Times (Based on Architecture)

#### Text Query Flow
```
Step                    | Expected Time | Confidence
------------------------|---------------|------------
WhatsApp → Lambda       | 200-500ms     | High
Lambda Cold Start       | 3-5s (first)  | High
Lambda Warm             | 50-100ms      | High
Bedrock API Call        | 1-3s          | High
DynamoDB Read/Write     | 10-50ms       | High
Response to WhatsApp    | 200-500ms     | High
------------------------|---------------|------------
Total (Cold Start)      | 5-9 seconds   | Medium
Total (Warm)            | 2-4 seconds   | High
```

#### Image Query Flow
```
Step                    | Expected Time | Confidence
------------------------|---------------|------------
Image Download          | 1-2s          | Medium
Kindwise API            | 3-5s          | High (API docs)
AI Response Gen         | 1-3s          | High
Total                   | 5-10 seconds  | Medium
```

### 3.2 Cost Projections (Based on AWS Pricing)

#### For 1,000 Users (300K queries/month)
```
Service              | Calculation                    | Monthly Cost
---------------------|--------------------------------|-------------
Lambda               | 300K × $0.20/1M                | $60 (~₹5,000)
DynamoDB             | 300K reads + 300K writes       | $3-5 (~₹250-400)
Bedrock Nova         | 300K × 500 tokens × $0.00008   | $12 (~₹1,000)
S3                   | 10GB storage + transfers       | $2 (~₹160)
Secrets Manager      | 5 secrets × $0.40              | $2 (~₹160)
WhatsApp API         | 300K messages × $0.005         | $1,500 (~₹125,000)
---------------------|--------------------------------|-------------
Total (estimated)    |                                | ~₹131,000
```

**Note**: WhatsApp API is the major cost (95% of total)

---

## 4. What We Need to Actually Test

### 4.1 Performance Testing Needed

❌ **Not Yet Tested**:
- Load testing (100+ concurrent users)
- Stress testing (finding breaking point)
- Endurance testing (24+ hours continuous)
- Geographic latency (different regions)
- Peak hour performance
- Failure recovery time

### 4.2 Accuracy Testing Needed

❌ **Not Yet Validated**:
- Disease detection accuracy (need expert validation)
- Price forecasting accuracy (need historical comparison)
- Budget planning accuracy (need farmer feedback)
- AI routing accuracy (need large sample size)

### 4.3 User Testing Needed

❌ **Not Yet Measured**:
- User satisfaction surveys (large sample)
- Feature adoption rates
- Retention rates (30-day, 90-day)
- Onboarding completion rates
- Drop-off analysis

---

## 5. Competitive Comparison (Realistic)

### 5.1 What We Can Claim

✅ **Verified Advantages**:
- WhatsApp-native (competitors require app download)
- Hindi support (many competitors are English-only)
- Serverless architecture (lower operational overhead)
- Multi-agent design (more specialized than single chatbot)
- Free for farmers (some competitors charge)

### 5.2 What We Cannot Claim Yet

❌ **Unverified Claims**:
- "Faster than competitors" (need side-by-side testing)
- "More accurate" (need validation studies)
- "Better user satisfaction" (need surveys)
- "Lower cost" (need actual cost data at scale)

---

## 6. Honest Assessment

### 6.1 What's Working Well

✅ **Proven**:
- System is functional and deployed
- WhatsApp integration works
- Onboarding flow works
- AI agents respond correctly
- DynamoDB stores data reliably
- Basic disease detection works
- Market price integration works

### 6.2 What's Untested

⚠️ **Unknown**:
- Performance at scale (100+ users)
- Accuracy in real-world conditions
- Cost at scale
- User satisfaction (large sample)
- System reliability over time
- Edge cases and error handling

### 6.3 Known Issues

❌ **Current Problems**:
- Cold starts cause 3-5s delay
- No load testing performed
- Limited user feedback
- No monitoring/alerting setup
- No automated testing
- No performance optimization done

---

## 7. Recommended Testing Plan

### Phase 1: Basic Performance Testing (1 week)

**Tasks**:
1. Set up CloudWatch dashboards
2. Monitor 100 real queries
3. Measure actual response times
4. Track error rates
5. Document cold start frequency

**Deliverable**: Actual performance baseline

### Phase 2: Load Testing (1 week)

**Tasks**:
1. Use Apache JMeter or Locust
2. Simulate 10, 50, 100 concurrent users
3. Measure response time degradation
4. Identify bottlenecks
5. Test failure scenarios

**Deliverable**: Scalability report

### Phase 3: Accuracy Validation (2 weeks)

**Tasks**:
1. Get 50+ disease images validated by experts
2. Compare price forecasts to actual prices
3. Validate budget calculations with farmers
4. Test AI routing with diverse queries
5. Measure false positive/negative rates

**Deliverable**: Accuracy report

### Phase 4: User Testing (2 weeks)

**Tasks**:
1. Recruit 50-100 real farmers
2. Conduct structured surveys
3. Track feature usage
4. Measure satisfaction
5. Collect improvement feedback

**Deliverable**: User experience report

---

## 8. What to Present at Hackathon

### 8.1 Honest Claims You Can Make

✅ **Safe to Claim**:
- "Functional WhatsApp-based AI system"
- "Multi-agent architecture with 3 specialized agents"
- "Serverless AWS infrastructure"
- "Hindi language support"
- "Disease detection, market prices, budget planning"
- "Deployed and working prototype"

### 8.2 Claims to Avoid (Without Data)

❌ **Don't Claim Without Evidence**:
- Specific response times (unless measured)
- Specific accuracy percentages (unless validated)
- "Tested with 1000+ farmers" (unless true)
- "99.9% uptime" (unless monitored)
- Specific cost savings (unless calculated)
- User satisfaction scores (unless surveyed)

### 8.3 How to Present Projections

✅ **Honest Framing**:
- "Based on AWS benchmarks, we expect..."
- "Our architecture is designed to achieve..."
- "Industry standards suggest..."
- "We project that at scale..."
- "Initial testing shows promising results..."

---

## 9. Actual Metrics You Can Measure Now

### 9.1 Quick Tests You Can Run Today

**Test 1: Response Time**
```bash
# Send 10 queries, measure time
# Use: time curl or Postman
Expected: 2-5 seconds (warm), 5-8 seconds (cold)
```

**Test 2: Error Rate**
```bash
# Check CloudWatch Logs for errors
# Count: successful vs failed requests
Expected: <1% error rate
```

**Test 3: Cost**
```bash
# Check AWS Cost Explorer
# Look at last 7 days
Expected: <$10 for prototype testing
```

**Test 4: User Feedback**
```bash
# Ask your 10-20 test users
# Simple 1-5 rating
Expected: 4+ rating if system works well
```

---

## 10. Conclusion (Realistic)

### Current Status

**What We Have**:
- ✅ Working prototype deployed on AWS
- ✅ Functional WhatsApp integration
- ✅ Multi-agent AI system
- ✅ Basic features implemented
- ✅ Small-scale testing completed

**What We Need**:
- ⚠️ Performance testing at scale
- ⚠️ Accuracy validation
- ⚠️ User testing (large sample)
- ⚠️ Cost validation
- ⚠️ Reliability testing

### Recommendation

**For Hackathon**: Present as a **working prototype with strong architecture** and **clear testing roadmap**. Be honest about what's tested vs projected.

**For Production**: Complete Phase 1-4 testing (6 weeks) before claiming specific performance metrics.

---

## Appendix: How to Get Real Metrics

### A. CloudWatch Queries

```sql
-- Average Lambda duration
fields @timestamp, @duration
| stats avg(@duration) as avg_duration, 
        max(@duration) as max_duration,
        min(@duration) as min_duration
| filter @type = "REPORT"
```

### B. Cost Analysis

```bash
# AWS CLI command
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-03-01 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

### C. User Testing Template

```
Survey Questions:
1. How easy was it to use? (1-5)
2. How fast were responses? (1-5)
3. How accurate was advice? (1-5)
4. Would you recommend? (Yes/No)
5. What needs improvement? (Open)
```

---

**This is an honest assessment. Use actual data when available, clearly label projections, and be transparent about what's tested vs estimated.**

**Last Updated**: March 7, 2026  
**Status**: Prototype - Needs Production Validation
