"""
WhatsApp Interactive Messages - Buttons, Lists, and Menus
"""

def create_language_selection():
    """Create language selection menu"""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "🌾 KisaanMitra"
            },
            "body": {
                "text": "*Welcome to KisaanMitra!*\n\nYour AI-powered farming assistant for:\n✓ Crop disease detection\n✓ Market prices\n✓ Budget planning\n✓ Weather alerts\n\n*Please select your language:*\nकृपया अपनी भाषा चुनें:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "lang_english",
                            "title": "🇬🇧 English"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "lang_hindi",
                            "title": "🇮🇳 हिंदी"
                        }
                    }
                ]
            }
        }
    }

def create_main_menu(language='hindi'):
    """Create main menu with interactive buttons"""
    if language == 'english':
        return {
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "🌾 KisaanMitra"
                },
                "body": {
                    "text": "*Main Menu*\n\nHow can I help you today?"
                },
                "footer": {
                    "text": "Powered by AI"
                },
                "action": {
                    "button": "Select Service",
                    "sections": [
                        {
                            "title": "Core Services",
                            "rows": [
                                {
                                    "id": "crop_health",
                                    "title": "🔍 Crop Health",
                                    "description": "Disease detection & treatment"
                                },
                                {
                                    "id": "market_price",
                                    "title": "📊 Market Prices",
                                    "description": "Live mandi rates"
                                },
                                {
                                    "id": "budget_plan",
                                    "title": "💰 Budget Planning",
                                    "description": "Crop cost & profit analysis"
                                }
                            ]
                        },
                        {
                            "title": "Additional Services",
                            "rows": [
                                {
                                    "id": "weather",
                                    "title": "🌤️ Weather Forecast",
                                    "description": "7-day weather & alerts"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    else:  # Hindi
        return {
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": "🌾 KisaanMitra"
                },
                "body": {
                    "text": "*मुख्य मेनू*\n\nमैं आपकी कैसे मदद कर सकता हूं?"
                },
                "footer": {
                    "text": "AI द्वारा संचालित"
                },
                "action": {
                    "button": "सेवा चुनें",
                    "sections": [
                        {
                            "title": "मुख्य सेवाएं",
                            "rows": [
                                {
                                    "id": "crop_health",
                                    "title": "🔍 फसल स्वास्थ्य",
                                    "description": "रोग पहचान और उपचार"
                                },
                                {
                                    "id": "market_price",
                                    "title": "📊 बाजार भाव",
                                    "description": "लाइव मंडी दरें"
                                },
                                {
                                    "id": "budget_plan",
                                    "title": "💰 बजट योजना",
                                    "description": "फसल लागत और लाभ विश्लेषण"
                                }
                            ]
                        },
                        {
                            "title": "अतिरिक्त सेवाएं",
                            "rows": [
                                {
                                    "id": "weather",
                                    "title": "🌤️ मौसम पूर्वानुमान",
                                    "description": "7 दिन का मौसम और अलर्ट"
                                }
                            ]
                        }
                    ]
                }
            }
        }


def create_crop_selection_list():
    """Create crop selection list"""
    return {
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {
                "type": "text",
                "text": "फसल चुनें"
            },
            "body": {
                "text": "कृपया अपनी फसल चुनें:"
            },
            "action": {
                "button": "फसल देखें",
                "sections": [
                    {
                        "title": "अनाज",
                        "rows": [
                            {"id": "rice", "title": "धान/चावल", "description": "Rice"},
                            {"id": "wheat", "title": "गेहूं", "description": "Wheat"},
                            {"id": "maize", "title": "मक्का", "description": "Maize"}
                        ]
                    },
                    {
                        "title": "सब्जियां",
                        "rows": [
                            {"id": "tomato", "title": "टमाटर", "description": "Tomato"},
                            {"id": "onion", "title": "प्याज", "description": "Onion"},
                            {"id": "potato", "title": "आलू", "description": "Potato"}
                        ]
                    },
                    {
                        "title": "नकदी फसलें",
                        "rows": [
                            {"id": "sugarcane", "title": "गन्ना", "description": "Sugarcane"},
                            {"id": "cotton", "title": "कपास", "description": "Cotton"},
                            {"id": "soybean", "title": "सोयाबीन", "description": "Soybean"}
                        ]
                    }
                ]
            }
        }
    }


def create_back_button(language='hindi'):
    """Create back to menu button with full navigation"""
    if language == 'english':
        return {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "What would you like to do next?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_back",
                                "title": "⬅ Back"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_home",
                                "title": "🏠 Home"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_cancel",
                                "title": "❌ Cancel"
                            }
                        }
                    ]
                }
            }
        }
    else:  # Hindi
        return {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": "आप क्या करना चाहेंगे?"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_back",
                                "title": "⬅ पीछे"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_home",
                                "title": "🏠 मुख्य मेनू"
                            }
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "nav_cancel",
                                "title": "❌ रद्द करें"
                            }
                        }
                    ]
                }
            }
        }


def create_quick_actions():
    """Create quick action buttons"""
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "त्वरित कार्य:"
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "today_price",
                            "title": "आज का भाव"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "weather",
                            "title": "मौसम"
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "crop_health",
                            "title": "🔍 फसल जांच"
                        }
                    }
                ]
            }
        }
    }


def create_confidence_response(disease, confidence, treatments):
    """Create disease detection response with confidence"""
    confidence_emoji = "🟢" if confidence > 80 else "🟡" if confidence > 60 else "🔴"
    
    message = f"{confidence_emoji} *रोग पहचान परिणाम*\n\n"
    message += f"*रोग*: {disease}\n"
    message += f"*विश्वास स्तर*: {confidence}%\n\n"
    
    if confidence > 80:
        message += "✅ उच्च विश्वास - निदान सटीक है\n\n"
    elif confidence > 60:
        message += "⚠️ मध्यम विश्वास - कृपया अधिक जानकारी दें\n\n"
    else:
        message += "❌ कम विश्वास - विशेषज्ञ से संपर्क करें\n\n"
    
    message += "*उपचार*:\n"
    for i, treatment in enumerate(treatments[:3], 1):
        message += f"{i}. {treatment}\n"
    
    return message


def send_interactive_message(to, phone_number_id, token, interactive_payload):
    """Send interactive message via WhatsApp API"""
    import urllib3
    import json
    
    http = urllib3.PoolManager()
    url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        **interactive_payload
    }
    
    response = http.request("POST", url, body=json.dumps(data), headers=headers)
    return response.status == 200



def add_navigation_text(message, language='hindi'):
    """Add navigation instructions to text message"""
    if language == 'english':
        nav_text = "\n\n💡 Type 'back' to go back, 'home' for main menu, or 'cancel' to restart."
    else:
        nav_text = "\n\n💡 'back' टाइप करें पीछे जाने के लिए, 'home' मुख्य मेनू के लिए, या 'cancel' पुनः आरंभ करने के लिए।"
    
    return message + nav_text
