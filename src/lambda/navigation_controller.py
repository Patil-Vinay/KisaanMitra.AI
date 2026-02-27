"""
Navigation Controller - Manages conversation flow and state
Provides Back/Home/Cancel navigation for WhatsApp bot
"""
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

class NavigationController:
    """Manages conversation navigation and state"""
    
    def __init__(self, user_id, table_name='kisaanmitra-navigation-state'):
        self.user_id = user_id
        self.table_name = table_name
        try:
            self.navigation_table = dynamodb.Table(table_name)
            self.state = self.load_state()
        except Exception as e:
            print(f"[NAV] Warning: Navigation table not available: {e}")
            self.navigation_table = None
            self.state = {'current_screen': 'main_menu', 'history': []}
    
    def load_state(self):
        """Load navigation state from DynamoDB"""
        if not self.navigation_table:
            return {'current_screen': 'main_menu', 'history': []}
        
        try:
            response = self.navigation_table.get_item(Key={'user_id': self.user_id})
            if 'Item' in response:
                return {
                    'current_screen': response['Item'].get('current_screen', 'main_menu'),
                    'history': response['Item'].get('history', [])
                }
        except Exception as e:
            print(f"[NAV] Error loading state: {e}")
        
        return {'current_screen': 'main_menu', 'history': []}
    
    def save_state(self):
        """Save navigation state to DynamoDB"""
        if not self.navigation_table:
            print(f"[NAV] Warning: Cannot save state - table not available")
            return
        
        try:
            self.navigation_table.put_item(Item={
                'user_id': self.user_id,
                'current_screen': self.state['current_screen'],
                'history': self.state['history'],
                'updated_at': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"[NAV] Error saving state: {e}")
    
    def navigate_to(self, screen):
        """Navigate to a new screen"""
        # Add current screen to history
        if self.state['current_screen'] != screen:
            history = self.state.get('history', [])
            history.append(self.state['current_screen'])
            self.state['history'] = history[-10:]  # Keep last 10
        
        self.state['current_screen'] = screen
        self.save_state()
        print(f"[NAV] Navigated to: {screen}")
    
    def go_back(self):
        """Go back to previous screen"""
        history = self.state.get('history', [])
        if history:
            previous = history.pop()
            self.state['current_screen'] = previous
            self.state['history'] = history
            self.save_state()
            print(f"[NAV] Went back to: {previous}")
            return previous
        print(f"[NAV] No history, returning to main_menu")
        return 'main_menu'
    
    def go_home(self):
        """Go to main menu"""
        self.state['current_screen'] = 'main_menu'
        self.state['history'] = []
        self.save_state()
        print(f"[NAV] Returned to home")
        return 'main_menu'
    
    def cancel(self):
        """Cancel and clear state"""
        self.state = {'current_screen': 'cancelled', 'history': []}
        self.save_state()
        print(f"[NAV] Cancelled and cleared state")
        return 'cancelled'
    
    def get_current_screen(self):
        """Get current screen"""
        return self.state.get('current_screen', 'main_menu')
    
    def add_navigation_buttons(self, message, language='hindi'):
        """Add navigation buttons to message"""
        if language == 'english':
            buttons = "\n\n[⬅ Back] [🏠 Home] [❌ Cancel]"
        else:
            buttons = "\n\n[⬅ पीछे] [🏠 मुख्य मेनू] [❌ रद्द करें]"
        
        return message + buttons
    
    def get_navigation_prompt(self, language='hindi'):
        """Get navigation prompt text"""
        if language == 'english':
            return "\n\nType 'back' to go back, 'home' for main menu, or 'cancel' to restart."
        else:
            return "\n\n'back' टाइप करें पीछे जाने के लिए, 'home' मुख्य मेनू के लिए, या 'cancel' पुनः आरंभ करने के लिए।"
