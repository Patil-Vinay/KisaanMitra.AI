"""
Comprehensive Agent Testing Framework
Tests all agents with 10 scenarios each in both languages
"""

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'lambda'))

# Test scenarios for each agent
TEST_SCENARIOS = {
    "crop_agent": {
        "english": [
            {
                "id": "crop_en_1",
                "input": "My tomato leaves are turning yellow",
                "expected_keywords": ["yellow", "leaves", "tomato", "nitrogen", "water"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_2",
                "input": "White spots on wheat crop",
                "expected_keywords": ["white", "spots", "wheat", "fungus", "disease"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_3",
                "input": "Cotton leaves have holes",
                "expected_keywords": ["holes", "cotton", "pest", "insect"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_4",
                "input": "Sugarcane turning brown",
                "expected_keywords": ["brown", "sugarcane", "disease"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_5",
                "input": "Rice plants not growing well",
                "expected_keywords": ["rice", "growth", "nutrient", "water"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_6",
                "input": "Black spots on potato leaves",
                "expected_keywords": ["black", "spots", "potato", "blight"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_7",
                "input": "Onion bulbs rotting",
                "expected_keywords": ["onion", "rot", "disease", "fungus"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_8",
                "input": "Chilli plants wilting",
                "expected_keywords": ["chilli", "wilt", "water", "disease"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_9",
                "input": "Soybean leaves curling",
                "expected_keywords": ["soybean", "curl", "pest", "virus"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "crop_en_10",
                "input": "Maize cobs have worms",
                "expected_keywords": ["maize", "worm", "pest", "insect"],
                "should_not_contain": ["hindi", "हिंदी"]
            }
        ],
        "hindi": [
            {
                "id": "crop_hi_1",
                "input": "मेरे टमाटर के पत्ते पीले हो रहे हैं",
                "expected_keywords": ["टमाटर", "पत्ते", "पीले"],
                "should_not_contain": ["english", "tomato"]
            },
            {
                "id": "crop_hi_2",
                "input": "गेहूं की फसल पर सफेद धब्बे",
                "expected_keywords": ["गेहूं", "धब्बे", "सफेद"],
                "should_not_contain": ["english", "wheat"]
            },
            {
                "id": "crop_hi_3",
                "input": "कपास के पत्तों में छेद हैं",
                "expected_keywords": ["कपास", "पत्तों", "छेद"],
                "should_not_contain": ["english", "cotton"]
            },
            {
                "id": "crop_hi_4",
                "input": "गन्ना भूरा हो रहा है",
                "expected_keywords": ["गन्ना", "भूरा"],
                "should_not_contain": ["english", "sugarcane"]
            },
            {
                "id": "crop_hi_5",
                "input": "धान के पौधे अच्छे से नहीं बढ़ रहे",
                "expected_keywords": ["धान", "पौधे", "बढ़"],
                "should_not_contain": ["english", "rice"]
            },
            {
                "id": "crop_hi_6",
                "input": "आलू के पत्तों पर काले धब्बे",
                "expected_keywords": ["आलू", "पत्तों", "काले"],
                "should_not_contain": ["english", "potato"]
            },
            {
                "id": "crop_hi_7",
                "input": "प्याज सड़ रहा है",
                "expected_keywords": ["प्याज", "सड़"],
                "should_not_contain": ["english", "onion"]
            },
            {
                "id": "crop_hi_8",
                "input": "मिर्च के पौधे मुरझा रहे हैं",
                "expected_keywords": ["मिर्च", "पौधे", "मुरझा"],
                "should_not_contain": ["english", "chilli"]
            },
            {
                "id": "crop_hi_9",
                "input": "सोयाबीन के पत्ते मुड़ रहे हैं",
                "expected_keywords": ["सोयाबीन", "पत्ते"],
                "should_not_contain": ["english", "soybean"]
            },
            {
                "id": "crop_hi_10",
                "input": "मक्का में कीड़े लग गए हैं",
                "expected_keywords": ["मक्का", "कीड़े"],
                "should_not_contain": ["english", "maize"]
            }
        ]
    },
    "market_agent": {
        "english": [
            {
                "id": "market_en_1",
                "input": "What is tomato price today?",
                "expected_keywords": ["tomato", "price", "₹"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_2",
                "input": "Onion market rate in Pune",
                "expected_keywords": ["onion", "price", "pune"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_3",
                "input": "Wheat mandi bhav",
                "expected_keywords": ["wheat", "price"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_4",
                "input": "Cotton selling price",
                "expected_keywords": ["cotton", "price"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_5",
                "input": "Rice market rate today",
                "expected_keywords": ["rice", "price", "market"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_6",
                "input": "Sugarcane price per ton",
                "expected_keywords": ["sugarcane", "price", "ton"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_7",
                "input": "Potato wholesale price",
                "expected_keywords": ["potato", "price"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_8",
                "input": "Soybean market rate in Maharashtra",
                "expected_keywords": ["soybean", "price", "maharashtra"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_9",
                "input": "Chilli price today",
                "expected_keywords": ["chilli", "price"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "market_en_10",
                "input": "Maize selling rate",
                "expected_keywords": ["maize", "price"],
                "should_not_contain": ["hindi", "हिंदी"]
            }
        ],
        "hindi": [
            {
                "id": "market_hi_1",
                "input": "टमाटर का भाव क्या है?",
                "expected_keywords": ["टमाटर", "भाव", "₹"],
                "should_not_contain": ["english", "tomato"]
            },
            {
                "id": "market_hi_2",
                "input": "प्याज की कीमत पुणे में",
                "expected_keywords": ["प्याज", "कीमत"],
                "should_not_contain": ["english", "onion"]
            },
            {
                "id": "market_hi_3",
                "input": "गेहूं का मंडी भाव",
                "expected_keywords": ["गेहूं", "भाव", "मंडी"],
                "should_not_contain": ["english", "wheat"]
            },
            {
                "id": "market_hi_4",
                "input": "कपास की बिक्री दर",
                "expected_keywords": ["कपास", "दर"],
                "should_not_contain": ["english", "cotton"]
            },
            {
                "id": "market_hi_5",
                "input": "चावल का बाजार भाव आज",
                "expected_keywords": ["चावल", "भाव", "बाजार"],
                "should_not_contain": ["english", "rice"]
            },
            {
                "id": "market_hi_6",
                "input": "गन्ने की कीमत प्रति टन",
                "expected_keywords": ["गन्ने", "कीमत", "टन"],
                "should_not_contain": ["english", "sugarcane"]
            },
            {
                "id": "market_hi_7",
                "input": "आलू का थोक भाव",
                "expected_keywords": ["आलू", "भाव"],
                "should_not_contain": ["english", "potato"]
            },
            {
                "id": "market_hi_8",
                "input": "सोयाबीन का बाजार भाव महाराष्ट्र में",
                "expected_keywords": ["सोयाबीन", "भाव", "महाराष्ट्र"],
                "should_not_contain": ["english", "soybean"]
            },
            {
                "id": "market_hi_9",
                "input": "मिर्च की कीमत आज",
                "expected_keywords": ["मिर्च", "कीमत"],
                "should_not_contain": ["english", "chilli"]
            },
            {
                "id": "market_hi_10",
                "input": "मक्का की बिक्री दर",
                "expected_keywords": ["मक्का", "दर"],
                "should_not_contain": ["english", "maize"]
            }
        ]
    },
    "finance_agent": {
        "english": [
            {
                "id": "finance_en_1",
                "input": "I need tomato budget for 2 acres in Pune",
                "expected_keywords": ["tomato", "budget", "cost", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_2",
                "input": "What is the cost of growing wheat on 5 acres?",
                "expected_keywords": ["wheat", "cost", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_3",
                "input": "Cotton cultivation budget for 3 acres in Nagpur",
                "expected_keywords": ["cotton", "budget", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_4",
                "input": "Sugarcane farming cost 1 acre Kolhapur",
                "expected_keywords": ["sugarcane", "cost", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_5",
                "input": "Rice cultivation expenses for 4 acres",
                "expected_keywords": ["rice", "expense", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_6",
                "input": "Onion farming budget 2 acres Mumbai",
                "expected_keywords": ["onion", "budget", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_7",
                "input": "Potato cultivation cost analysis 3 acres",
                "expected_keywords": ["potato", "cost", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_8",
                "input": "Soybean farming budget 5 acres Maharashtra",
                "expected_keywords": ["soybean", "budget", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_9",
                "input": "Chilli cultivation expenses 1 acre",
                "expected_keywords": ["chilli", "expense", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "finance_en_10",
                "input": "Maize farming cost 2 acres Nashik",
                "expected_keywords": ["maize", "cost", "₹", "acre"],
                "should_not_contain": ["hindi", "हिंदी"]
            }
        ],
        "hindi": [
            {
                "id": "finance_hi_1",
                "input": "मुझे टमाटर के लिए 2 एकड़ पुणे में बजट चाहिए",
                "expected_keywords": ["टमाटर", "बजट", "₹", "एकड़"],
                "should_not_contain": ["english", "tomato"]
            },
            {
                "id": "finance_hi_2",
                "input": "5 एकड़ में गेहूं उगाने की लागत क्या है?",
                "expected_keywords": ["गेहूं", "लागत", "₹", "एकड़"],
                "should_not_contain": ["english", "wheat"]
            },
            {
                "id": "finance_hi_3",
                "input": "नागपुर में 3 एकड़ कपास की खेती का बजट",
                "expected_keywords": ["कपास", "बजट", "₹", "एकड़"],
                "should_not_contain": ["english", "cotton"]
            },
            {
                "id": "finance_hi_4",
                "input": "कोल्हापुर में 1 एकड़ गन्ने की खेती की लागत",
                "expected_keywords": ["गन्ने", "लागत", "₹", "एकड़"],
                "should_not_contain": ["english", "sugarcane"]
            },
            {
                "id": "finance_hi_5",
                "input": "4 एकड़ धान की खेती का खर्च",
                "expected_keywords": ["धान", "खर्च", "₹", "एकड़"],
                "should_not_contain": ["english", "rice"]
            },
            {
                "id": "finance_hi_6",
                "input": "मुंबई में 2 एकड़ प्याज की खेती का बजट",
                "expected_keywords": ["प्याज", "बजट", "₹", "एकड़"],
                "should_not_contain": ["english", "onion"]
            },
            {
                "id": "finance_hi_7",
                "input": "3 एकड़ आलू की खेती की लागत विश्लेषण",
                "expected_keywords": ["आलू", "लागत", "₹", "एकड़"],
                "should_not_contain": ["english", "potato"]
            },
            {
                "id": "finance_hi_8",
                "input": "महाराष्ट्र में 5 एकड़ सोयाबीन की खेती का बजट",
                "expected_keywords": ["सोयाबीन", "बजट", "₹", "एकड़"],
                "should_not_contain": ["english", "soybean"]
            },
            {
                "id": "finance_hi_9",
                "input": "1 एकड़ मिर्च की खेती का खर्च",
                "expected_keywords": ["मिर्च", "खर्च", "₹", "एकड़"],
                "should_not_contain": ["english", "chilli"]
            },
            {
                "id": "finance_hi_10",
                "input": "नाशिक में 2 एकड़ मक्का की खेती की लागत",
                "expected_keywords": ["मक्का", "लागत", "₹", "एकड़"],
                "should_not_contain": ["english", "maize"]
            }
        ]
    },
    "general_agent": {
        "english": [
            {
                "id": "general_en_1",
                "input": "Hello, how are you?",
                "expected_keywords": ["hello", "help", "kisaan"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_2",
                "input": "What can you do?",
                "expected_keywords": ["help", "crop", "market", "budget"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_3",
                "input": "Tell me about farming",
                "expected_keywords": ["farm", "crop", "agriculture"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_4",
                "input": "What is the weather like?",
                "expected_keywords": ["weather", "forecast"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_5",
                "input": "I need help with my farm",
                "expected_keywords": ["help", "farm", "specific"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_6",
                "input": "Thank you for your help",
                "expected_keywords": ["welcome", "help"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_7",
                "input": "What is agriculture?",
                "expected_keywords": ["agriculture", "farm", "crop"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_8",
                "input": "How do I start farming?",
                "expected_keywords": ["start", "farm", "crop", "land"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_9",
                "input": "What is organic farming?",
                "expected_keywords": ["organic", "farm", "natural"],
                "should_not_contain": ["hindi", "हिंदी"]
            },
            {
                "id": "general_en_10",
                "input": "Tell me about irrigation",
                "expected_keywords": ["irrigation", "water", "farm"],
                "should_not_contain": ["hindi", "हिंदी"]
            }
        ],
        "hindi": [
            {
                "id": "general_hi_1",
                "input": "नमस्ते, आप कैसे हैं?",
                "expected_keywords": ["नमस्ते", "मदद", "किसान"],
                "should_not_contain": ["english", "hello"]
            },
            {
                "id": "general_hi_2",
                "input": "आप क्या कर सकते हैं?",
                "expected_keywords": ["मदद", "फसल", "बाजार", "बजट"],
                "should_not_contain": ["english", "help"]
            },
            {
                "id": "general_hi_3",
                "input": "मुझे खेती के बारे में बताएं",
                "expected_keywords": ["खेती", "फसल", "कृषि"],
                "should_not_contain": ["english", "farming"]
            },
            {
                "id": "general_hi_4",
                "input": "मौसम कैसा है?",
                "expected_keywords": ["मौसम"],
                "should_not_contain": ["english", "weather"]
            },
            {
                "id": "general_hi_5",
                "input": "मुझे अपने खेत में मदद चाहिए",
                "expected_keywords": ["मदद", "खेत"],
                "should_not_contain": ["english", "farm"]
            },
            {
                "id": "general_hi_6",
                "input": "आपकी मदद के लिए धन्यवाद",
                "expected_keywords": ["धन्यवाद", "स्वागत"],
                "should_not_contain": ["english", "thank"]
            },
            {
                "id": "general_hi_7",
                "input": "कृषि क्या है?",
                "expected_keywords": ["कृषि", "खेती", "फसल"],
                "should_not_contain": ["english", "agriculture"]
            },
            {
                "id": "general_hi_8",
                "input": "मैं खेती कैसे शुरू करूं?",
                "expected_keywords": ["खेती", "शुरू", "फसल"],
                "should_not_contain": ["english", "farming"]
            },
            {
                "id": "general_hi_9",
                "input": "जैविक खेती क्या है?",
                "expected_keywords": ["जैविक", "खेती"],
                "should_not_contain": ["english", "organic"]
            },
            {
                "id": "general_hi_10",
                "input": "सिंचाई के बारे में बताएं",
                "expected_keywords": ["सिंचाई", "पानी"],
                "should_not_contain": ["english", "irrigation"]
            }
        ]
    }
}


def get_all_scenarios():
    """Get all test scenarios organized by agent and language"""
    return TEST_SCENARIOS


def get_scenarios_by_agent(agent_name):
    """Get scenarios for a specific agent"""
    return TEST_SCENARIOS.get(agent_name, {})


def get_total_scenario_count():
    """Get total number of test scenarios"""
    total = 0
    for agent in TEST_SCENARIOS.values():
        for lang in agent.values():
            total += len(lang)
    return total


if __name__ == "__main__":
    print(f"Total test scenarios: {get_total_scenario_count()}")
    for agent_name, agent_data in TEST_SCENARIOS.items():
        english_count = len(agent_data.get('english', []))
        hindi_count = len(agent_data.get('hindi', []))
        print(f"{agent_name}: {english_count} English + {hindi_count} Hindi = {english_count + hindi_count} total")
