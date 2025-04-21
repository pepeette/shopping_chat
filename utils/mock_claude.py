import re
import json
import random

class MockClaude:
    """
    A class that simulates Claude's responses for water filter recommendations
    """
    def __init__(self):
        self.conversation_state = "greeting"
        self.gathered_info = {
            "installation": None,
            "budget": None,
            "contaminants": None,
            "eco_friendly": None,
            "remineralization": None,
            "household_size": None
        }
    
    def get_response(self, user_input):
        """
        Generate a mock response based on conversation state and user input
        """
        user_input = user_input.lower()
        
        # Check for conversation reset
        if "start over" in user_input or "reset" in user_input:
            self.conversation_state = "greeting"
            self.gathered_info = {
                "installation": None,
                "budget": None,
                "contaminants": None,
                "eco_friendly": None,
                "remineralization": None,
                "household_size": None
            }
            return "Let's start over. How can I help you find the right water filter today?"
        
        # Handle different conversation states
        if self.conversation_state == "greeting":
            self.conversation_state = "ask_installation"
            return "Hello! I'm your water filter shopping assistant. I'll help you find the perfect water filtration solution for your needs. Where would you like to install your water filter? (under sink, countertop, pitcher, portable, shower, whole house)"
        
        elif self.conversation_state == "ask_installation":
            # Extract installation preferences
            installations = []
            if "under" in user_input and "sink" in user_input:
                installations.append("under_sink")
            if "counter" in user_input or "top" in user_input:
                installations.append("countertop")
            if "pitcher" in user_input or "jug" in user_input:
                installations.append("pitcher")
            if "portable" in user_input:
                installations.append("portable")
            if "shower" in user_input:
                installations.append("shower")
            if "whole" in user_input and "house" in user_input:
                installations.append("whole_house")
            
            # If no installation type detected, use default
            if not installations and not "don't know" in user_input and not "not sure" in user_input:
                # Try to infer from context
                if "kitchen" in user_input:
                    installations = ["countertop", "under_sink"]
                elif "travel" in user_input:
                    installations = ["portable"]
                elif "bathroom" in user_input:
                    installations = ["shower"]
            
            # If still no installation type, use all
            if not installations:
                installations = ["under_sink", "countertop", "pitcher", "portable"]
            
            self.gathered_info["installation"] = installations
            self.conversation_state = "ask_budget"
            return "Thanks! What's your budget for the water filter? Do you have a maximum price in mind?"
        
        elif self.conversation_state == "ask_budget":
            # Try to extract budget
            price_match = re.search(r'(\d+)', user_input)
            if price_match:
                price = int(price_match.group(1))
                # If they mention pounds or GBP, use as is
                if "£" in user_input or "pound" in user_input or "gbp" in user_input:
                    self.gathered_info["budget"] = price
                # If they mention dollars or USD, convert approximately
                elif "$" in user_input or "dollar" in user_input or "usd" in user_input:
                    self.gathered_info["budget"] = int(price * 0.8)  # Rough conversion
                else:
                    # Default to assuming GBP
                    self.gathered_info["budget"] = price
            else:
                # Handle vague budget references
                if "cheap" in user_input or "low" in user_input or "budget" in user_input:
                    self.gathered_info["budget"] = 50
                elif "mid" in user_input or "reasonable" in user_input:
                    self.gathered_info["budget"] = 150
                elif "expensive" in user_input or "high" in user_input or "premium" in user_input:
                    self.gathered_info["budget"] = 350
                else:
                    # Default
                    self.gathered_info["budget"] = 200
            
            self.conversation_state = "ask_contaminants"
            return "Got it. What contaminants are you most concerned about removing from your water? (e.g., chlorine, lead, fluoride, bacteria)"
        
        elif self.conversation_state == "ask_contaminants":
            contaminants = {
                "remove_chlorine": "chlorine" in user_input,
                "remove_lead": "lead" in user_input,
                "remove_fluoride": "fluoride" in user_input,
                "remove_bacteria": "bacteria" in user_input or "germs" in user_input or "microbes" in user_input
            }
            
            # If nothing specific is mentioned but general concerns are
            if not any(contaminants.values()):
                if "everything" in user_input or "all" in user_input or "maximum" in user_input:
                    contaminants = {
                        "remove_chlorine": True,
                        "remove_lead": True,
                        "remove_fluoride": True,
                        "remove_bacteria": True
                    }
                elif "taste" in user_input or "smell" in user_input or "odor" in user_input:
                    contaminants = {
                        "remove_chlorine": True,
                        "remove_lead": False,
                        "remove_fluoride": False,
                        "remove_bacteria": False
                    }
                elif "health" in user_input or "safety" in user_input:
                    contaminants = {
                        "remove_chlorine": True,
                        "remove_lead": True,
                        "remove_fluoride": False,
                        "remove_bacteria": True
                    }
            
            self.gathered_info["contaminants"] = contaminants
            self.conversation_state = "ask_eco"
            return "Is eco-friendliness important to you? Would you prefer a filter with minimal environmental impact or longer filter life to reduce waste?"
        
        elif self.conversation_state == "ask_eco":
            eco_friendly = False
            if any(term in user_input for term in ["eco", "environment", "planet", "green", "sustainable", "yes"]):
                eco_friendly = True
            
            self.gathered_info["eco_friendly"] = eco_friendly
            self.conversation_state = "ask_remineralization"
            return "Some filters add minerals back into the water after filtration. Is remineralization important to you for taste or health benefits?"
        
        elif self.conversation_state == "ask_remineralization":
            remineralization = False
            if any(term in user_input for term in ["mineral", "yes", "important", "health", "taste", "alkaline"]):
                remineralization = True
            
            self.gathered_info["remineralization"] = remineralization
            self.conversation_state = "ask_household"
            return "How many people will be using this water filter? This helps determine the capacity needed."
        
        elif self.conversation_state == "ask_household":
            # Try to extract household size
            size_match = re.search(r'(\d+)', user_input)
            if size_match:
                household_size = int(size_match.group(1))
            else:
                # Handle vague size references
                if any(term in user_input for term in ["just me", "only me", "myself", "alone", "single"]):
                    household_size = 1
                elif any(term in user_input for term in ["couple", "two", "2"]):
                    household_size = 2
                elif any(term in user_input for term in ["family", "several", "many"]):
                    household_size = 4
                else:
                    # Default
                    household_size = 3
            
            self.gathered_info["household_size"] = household_size
            
            # Determine priorities based on conversation
            priorities = []
            
            if self.gathered_info["contaminants"].get("remove_lead", False) or \
               self.gathered_info["contaminants"].get("remove_bacteria", False):
                priorities.append("health")
            
            if self.gathered_info["eco_friendly"]:
                priorities.append("eco")
            
            if self.gathered_info["budget"] < 100:
                priorities.append("price")
            
            # Add maintenance as a priority for larger households
            if self.gathered_info["household_size"] > 2:
                priorities.append("maintenance")
            
            # Ensure at least one priority
            if not priorities:
                priorities = ["health"]
            
            # Generate requirements JSON
            requirements = {
                "installation": self.gathered_info["installation"],
                "max_price": self.gathered_info["budget"],
                "remove_chlorine": self.gathered_info["contaminants"].get("remove_chlorine", True),
                "remove_lead": self.gathered_info["contaminants"].get("remove_lead", False),
                "remove_fluoride": self.gathered_info["contaminants"].get("remove_fluoride", False),
                "remove_bacteria": self.gathered_info["contaminants"].get("remove_bacteria", False),
                "eco_friendly": self.gathered_info["eco_friendly"],
                "remineralization": self.gathered_info["remineralization"],
                "priorities": priorities
            }
            
            # Reset for next conversation
            self.conversation_state = "greeting"
            
            # Return summary with JSON
            response = "Thank you for providing all that information! Based on what you've told me, I understand you're looking for:\n\n"
            response += f"- Installation type: {', '.join(requirements['installation'])}\n"
            response += f"- Budget: £{requirements['max_price']}\n"
            response += f"- Priorities: {', '.join(requirements['priorities'])}\n\n"
            response += "I've analyzed your requirements and here are my recommendations:\n\n"
            response += "```json\n"
            response += json.dumps(requirements, indent=2)
            response += "\n```"
            
            return response

# Initialize mock Claude
mock_claude = MockClaude()

def get_mock_response(user_input):
    """
    Get a response from mock Claude
    """
    return mock_claude.get_response(user_input)