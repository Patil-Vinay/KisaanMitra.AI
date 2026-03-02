"""
Hyperlocal Disease Tracking & Best Practices System
Tracks diseases in villages and shares successful treatments
"""

import boto3
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json

dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

disease_reports_table = dynamodb.Table('kisaanmitra-disease-reports')
treatment_success_table = dynamodb.Table('kisaanmitra-treatment-success')
best_practices_table = dynamodb.Table('kisaanmitra-best-practices')


class HyperlocalDiseaseTracker:
    """Track diseases and treatments in local farming communities"""
    
    def report_disease(self, user_id, village, district, crop, disease_name, 
                      severity, symptoms, image_url=None, send_alerts=True):
        """
        Farmer reports a disease they're experiencing
        
        Args:
            user_id: Farmer's phone number
            village: Village name
            district: District name
            crop: Affected crop
            disease_name: Disease identified (from AI or farmer)
            severity: low/medium/high
            symptoms: Description of symptoms
            image_url: S3 URL of disease image (optional)
            send_alerts: Whether to send alerts to nearby farmers (default True)
        
        Returns:
            tuple: (report_id, farmers_to_alert)
        """
        report_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        report = {
            'report_id': report_id,
            'user_id': user_id,
            'village': village,
            'district': district,
            'crop': crop,
            'disease_name': disease_name,
            'severity': severity,
            'symptoms': symptoms,
            'image_url': image_url,
            'timestamp': timestamp,
            'status': 'active',  # active, resolved, ongoing
            'treatment_applied': None,
            'resolution_notes': None,
            'alerts_sent': 0
        }
        
        disease_reports_table.put_item(Item=report)
        print(f"[HYPERLOCAL] Disease reported: {disease_name} in {village}")
        
        # Get list of farmers to alert (if enabled)
        farmers_to_alert = []
        if send_alerts:
            farmers_to_alert = self.get_farmers_to_alert(village, district, crop, user_id)
            print(f"[HYPERLOCAL] Found {len(farmers_to_alert)} farmers to alert")
        
        return report_id, farmers_to_alert
    
    def get_nearby_diseases(self, village, district, days=30, crop=None):
        """
        Get recent disease reports from the same village/district
        
        Args:
            village: Village name
            district: District name
            days: Look back period (default 30 days)
            crop: Filter by specific crop (optional)
        
        Returns:
            List of disease reports with treatment info
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        try:
            # Query by village
            response = disease_reports_table.query(
                IndexName='village-timestamp-index',
                KeyConditionExpression='village = :v AND #ts > :cutoff',
                ExpressionAttributeNames={'#ts': 'timestamp'},
                ExpressionAttributeValues={
                    ':v': village,
                    ':cutoff': cutoff_date
                }
            )
            
            reports = response.get('Items', [])
            
            # Filter by crop if specified
            if crop:
                reports = [r for r in reports if r.get('crop', '').lower() == crop.lower()]
            
            # Sort by timestamp (most recent first)
            reports.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            print(f"[HYPERLOCAL] Found {len(reports)} disease reports in {village}")
            return reports
            
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to get nearby diseases: {e}")
            return []
    
    def record_treatment_success(self, report_id, user_id, disease_name, 
                                treatment_method, effectiveness_score, 
                                cost, duration_days, notes):
        """
        Record a successful treatment (what worked for a farmer)
        
        Args:
            report_id: Original disease report ID
            user_id: Farmer who applied treatment
            disease_name: Disease that was treated
            treatment_method: What they did (pesticide, organic, etc)
            effectiveness_score: 1-10 rating
            cost: Treatment cost in rupees
            duration_days: How long until resolved
            notes: Additional details
        """
        success_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        success_record = {
            'success_id': success_id,
            'report_id': report_id,
            'user_id': user_id,
            'disease_type': disease_name,
            'treatment_method': treatment_method,
            'effectiveness_score': Decimal(str(effectiveness_score)),
            'cost_rupees': Decimal(str(cost)),
            'duration_days': duration_days,
            'notes': notes,
            'timestamp': timestamp,
            'verified': False,  # Can be verified by agricultural experts
            'upvotes': 0
        }
        
        treatment_success_table.put_item(Item=success_record)
        
        # Update original report
        try:
            disease_reports_table.update_item(
                Key={'report_id': report_id},
                UpdateExpression='SET #status = :status, treatment_applied = :treatment, resolution_notes = :notes',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'resolved',
                    ':treatment': treatment_method,
                    ':notes': notes
                }
            )
        except:
            pass
        
        print(f"[HYPERLOCAL] Treatment success recorded: {treatment_method} for {disease_name}")
        return success_id
    
    def get_successful_treatments(self, disease_name, min_score=7):
        """
        Get treatments that worked well for a specific disease
        
        Args:
            disease_name: Disease to find treatments for
            min_score: Minimum effectiveness score (default 7/10)
        
        Returns:
            List of successful treatments, sorted by effectiveness
        """
        try:
            response = treatment_success_table.query(
                IndexName='disease-effectiveness-index',
                KeyConditionExpression='disease_type = :disease AND effectiveness_score >= :score',
                ExpressionAttributeValues={
                    ':disease': disease_name,
                    ':score': Decimal(str(min_score))
                },
                ScanIndexForward=False  # Descending order (highest score first)
            )
            
            treatments = response.get('Items', [])
            print(f"[HYPERLOCAL] Found {len(treatments)} successful treatments for {disease_name}")
            return treatments
            
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to get treatments: {e}")
            return []
    
    def add_best_practice(self, user_id, village, crop_type, category, 
                         title, description, season=None):
        """
        Add a farming best practice from community knowledge
        
        Args:
            user_id: Farmer sharing the practice
            village: Their village
            crop_type: Crop this applies to
            category: pest_control, irrigation, fertilizer, harvesting, etc
            title: Short title
            description: Detailed description
            season: Applicable season (optional)
        """
        practice_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        practice = {
            'practice_id': practice_id,
            'user_id': user_id,
            'village': village,
            'crop_type': crop_type,
            'category': category,
            'title': title,
            'description': description,
            'season': season,
            'timestamp': timestamp,
            'upvotes': 0,
            'downvotes': 0,
            'verified': False
        }
        
        best_practices_table.put_item(Item=practice)
        print(f"[HYPERLOCAL] Best practice added: {title}")
        return practice_id
    
    def get_best_practices(self, crop_type, category=None, min_upvotes=0):
        """
        Get best practices for a crop
        
        Args:
            crop_type: Crop to get practices for
            category: Filter by category (optional)
            min_upvotes: Minimum upvotes (default 0)
        
        Returns:
            List of best practices, sorted by upvotes
        """
        try:
            response = best_practices_table.query(
                IndexName='crop-upvotes-index',
                KeyConditionExpression='crop_type = :crop AND upvotes >= :votes',
                ExpressionAttributeValues={
                    ':crop': crop_type,
                    ':votes': min_upvotes
                },
                ScanIndexForward=False  # Descending order (most upvotes first)
            )
            
            practices = response.get('Items', [])
            
            # Filter by category if specified
            if category:
                practices = [p for p in practices if p.get('category') == category]
            
            print(f"[HYPERLOCAL] Found {len(practices)} best practices for {crop_type}")
            return practices
            
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to get best practices: {e}")
            return []
    
    def upvote_practice(self, practice_id):
        """Upvote a best practice"""
        try:
            best_practices_table.update_item(
                Key={'practice_id': practice_id},
                UpdateExpression='SET upvotes = upvotes + :inc',
                ExpressionAttributeValues={':inc': 1}
            )
            print(f"[HYPERLOCAL] Practice upvoted: {practice_id}")
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to upvote: {e}")
    
    def get_farmers_to_alert(self, village, district, crop, reporter_user_id):
        """
        Get list of farmers in the same village growing the same crop
        (excluding the reporter)
        
        Args:
            village: Village name
            district: District name
            crop: Crop type
            reporter_user_id: User ID of the farmer who reported (to exclude)
        
        Returns:
            List of farmer profiles to send alerts to
        """
        try:
            # Import onboarding manager to query farmer profiles
            from onboarding.farmer_onboarding import onboarding_manager
            
            # Get all farmers in the village
            farmers = onboarding_manager.get_farmers_by_location(village, district)
            
            # Filter by crop and exclude reporter
            farmers_to_alert = []
            for farmer in farmers:
                # Skip the reporter
                if farmer.get('user_id') == reporter_user_id:
                    continue
                
                # Check if farmer grows this crop
                current_crops = farmer.get('current_crops', '').lower()
                if crop.lower() in current_crops:
                    farmers_to_alert.append(farmer)
            
            print(f"[HYPERLOCAL] Found {len(farmers_to_alert)} farmers in {village} growing {crop}")
            return farmers_to_alert
            
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to get farmers to alert: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_disease_alert_notification(self, disease_name, severity, village, 
                                         reporter_name, crop, language='english'):
        """
        Format a disease alert notification message for nearby farmers
        
        Args:
            disease_name: Name of the disease
            severity: low/medium/high
            village: Village where disease was reported
            reporter_name: Name of farmer who reported (optional, can be "A farmer")
            crop: Affected crop
            language: Message language
        
        Returns:
            Formatted alert message
        """
        severity_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }
        emoji = severity_emoji.get(severity, '⚠️')
        
        if language == 'hindi':
            msg = f"{emoji} *रोग चेतावनी - {village}*\n\n"
            msg += f"एक किसान ने {crop} में *{disease_name}* की रिपोर्ट की है।\n\n"
            msg += f"गंभीरता: {severity.upper()}\n\n"
            msg += f"💡 *सलाह*:\n"
            msg += f"• अपनी फसल की जांच करें\n"
            msg += f"• यदि लक्षण दिखें तो तुरंत उपचार करें\n"
            msg += f"• 'इलाज' टाइप करें सफल उपचार देखने के लिए\n\n"
            msg += f"📸 फसल की फोटो भेजें विस्तृत जांच के लिए"
        else:
            msg = f"{emoji} *Disease Alert - {village}*\n\n"
            msg += f"A farmer reported *{disease_name}* in {crop}.\n\n"
            msg += f"Severity: {severity.upper()}\n\n"
            msg += f"💡 *What to do*:\n"
            msg += f"• Check your crop immediately\n"
            msg += f"• Apply treatment if you see symptoms\n"
            msg += f"• Type 'treatment' to see what worked for others\n\n"
            msg += f"📸 Send a photo of your crop for detailed analysis"
        
        return msg
    
    def update_alerts_sent_count(self, report_id, count):
        """Update the number of alerts sent for a disease report"""
        try:
            disease_reports_table.update_item(
                Key={'report_id': report_id},
                UpdateExpression='SET alerts_sent = :count',
                ExpressionAttributeValues={':count': count}
            )
            print(f"[HYPERLOCAL] Updated alerts_sent to {count} for report {report_id}")
        except Exception as e:
            print(f"[HYPERLOCAL ERROR] Failed to update alerts count: {e}")
    
    def format_disease_alert(self, village, crop, language='english'):
        """
        Format a disease alert message for farmers
        Shows what diseases are active in their area
        """
        reports = self.get_nearby_diseases(village, None, days=7, crop=crop)
        
        if not reports:
            if language == 'hindi':
                return f"✅ अच्छी खबर! {village} में {crop} में कोई बीमारी रिपोर्ट नहीं हुई है।"
            return f"✅ Good news! No diseases reported for {crop} in {village} recently."
        
        # Group by disease
        disease_counts = {}
        for report in reports:
            disease = report.get('disease_name', 'Unknown')
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        if language == 'hindi':
            msg = f"⚠️ *{village} में रोग चेतावनी*\n\n"
            msg += f"पिछले 7 दिनों में {crop} की फसल में:\n\n"
            for disease, count in disease_counts.items():
                msg += f"🔴 *{disease}*: {count} किसान प्रभावित\n"
        else:
            msg = f"⚠️ *Disease Alert: {village}*\n\n"
            msg += f"Recent reports in {crop} (last 7 days):\n\n"
            for disease, count in disease_counts.items():
                msg += f"🔴 *{disease}*: {count} farmer(s) affected\n"
        
        return msg
    
    def format_treatment_recommendations(self, disease_name, language='english'):
        """
        Format treatment recommendations based on what worked for other farmers
        """
        treatments = self.get_successful_treatments(disease_name, min_score=7)
        
        if not treatments:
            if language == 'hindi':
                return f"❌ *{disease_name}*: अभी तक कोई सफल उपचार रिकॉर्ड नहीं है।\n   💡 कृपया कृषि विशेषज्ञ से संपर्क करें।"
            return f"❌ *{disease_name}*: No proven treatments recorded yet.\n   💡 Please consult an agricultural expert."
        
        if language == 'hindi':
            msg = f"✅ *{disease_name} - सफल उपचार*\n\n"
            msg += f"आपके क्षेत्र के किसानों ने ये उपचार सफल पाए:\n\n"
        else:
            msg = f"✅ *{disease_name} - Proven Treatments*\n\n"
            msg += f"What worked for farmers in your area:\n\n"
        
        for i, treatment in enumerate(treatments[:3], 1):  # Top 3
            score = float(treatment.get('effectiveness_score', 0))
            method = treatment.get('treatment_method', 'Unknown')
            cost = float(treatment.get('cost_rupees', 0))
            days = treatment.get('duration_days', 'N/A')
            notes = treatment.get('notes', '')
            
            if language == 'hindi':
                msg += f"*{i}. {method}*\n"
                msg += f"   • प्रभावशीलता: {score}/10 ⭐\n"
                msg += f"   • लागत: ₹{cost:.0f}\n"
                msg += f"   • समय: {days} दिन\n"
                if notes:
                    msg += f"   • टिप: {notes}\n"
                msg += "\n"
            else:
                msg += f"*{i}. {method}*\n"
                msg += f"   • Effectiveness: {score}/10 ⭐\n"
                msg += f"   • Cost: ₹{cost:.0f}\n"
                msg += f"   • Duration: {days} days\n"
                if notes:
                    msg += f"   • Tip: {notes}\n"
                msg += "\n"
        
        return msg


# Global instance
hyperlocal_tracker = HyperlocalDiseaseTracker()
