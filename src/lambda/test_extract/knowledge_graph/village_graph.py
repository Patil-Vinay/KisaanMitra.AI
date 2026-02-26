"""
Village Knowledge Graph Module
Manages farmer data in Amazon Neptune graph database
"""

import json
import boto3
from datetime import datetime
from typing import Dict, List, Optional
from gremlin_python.driver import client, serializer
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Configuration
NEPTUNE_ENDPOINT = "your-neptune-cluster.cluster-xxxxx.ap-south-1.neptune.amazonaws.com"
NEPTUNE_PORT = 8182


class VillageKnowledgeGraph:
    """Manages village-level knowledge graph in Neptune"""
    
    def __init__(self, neptune_endpoint: str = None, neptune_port: int = 8182):
        """Initialize Neptune connection"""
        self.endpoint = neptune_endpoint or NEPTUNE_ENDPOINT
        self.port = neptune_port
        self.connection_string = f"wss://{self.endpoint}:{self.port}/gremlin"
        
        # For local testing without Neptune, use in-memory storage
        self.use_neptune = neptune_endpoint is not None
        self.local_graph = {"farmers": [], "villages": [], "crops": []}
    
    def get_connection(self):
        """Get Gremlin connection to Neptune"""
        if not self.use_neptune:
            return None
        
        try:
            return DriverRemoteConnection(
                self.connection_string,
                'g',
                message_serializer=serializer.GraphSONSerializersV2d0()
            )
        except Exception as e:
            print(f"Neptune connection error: {e}")
            return None
    
    def add_farmer_to_graph(self, user_profile: Dict) -> bool:
        """
        Add farmer node to knowledge graph with relationships
        
        Graph Structure:
        (Farmer) -[LIVES_IN]-> (Village)
        (Farmer) -[GROWS]-> (Crop)
        (Village) -[HAS_FARMER]-> (Farmer)
        (Crop) -[GROWN_BY]-> (Farmer)
        """
        
        if self.use_neptune:
            return self._add_to_neptune(user_profile)
        else:
            return self._add_to_local_graph(user_profile)
    
    def _add_to_neptune(self, profile: Dict) -> bool:
        """Add farmer to Neptune graph database"""
        try:
            conn = self.get_connection()
            if not conn:
                print("No Neptune connection, using local storage")
                return self._add_to_local_graph(profile)
            
            g = traversal().withRemote(conn)
            
            user_id = profile.get("user_id")
            name = profile.get("name")
            village = profile.get("village")
            crops = profile.get("crops", "").split(",")
            land_acres = profile.get("land_acres")
            phone = profile.get("phone")
            
            # Create or update Farmer node
            farmer = g.V().has('farmer', 'user_id', user_id).fold().coalesce(
                __.unfold(),
                __.addV('farmer').property('user_id', user_id)
            ).property('name', name).property('phone', phone).property('land_acres', land_acres).property('registered_at', profile.get('registered_at')).next()
            
            # Create or get Village node
            village_node = g.V().has('village', 'name', village).fold().coalesce(
                __.unfold(),
                __.addV('village').property('name', village)
            ).next()
            
            # Create LIVES_IN relationship
            g.V(farmer).outE('LIVES_IN').drop().iterate()
            g.V(farmer).addE('LIVES_IN').to(village_node).iterate()
            
            # Create or get Crop nodes and relationships
            for crop in crops:
                crop = crop.strip()
                if crop:
                    crop_node = g.V().has('crop', 'name', crop).fold().coalesce(
                        __.unfold(),
                        __.addV('crop').property('name', crop)
                    ).next()
                    
                    # Create GROWS relationship
                    g.V(farmer).outE('GROWS').where(__.inV().has('name', crop)).drop().iterate()
                    g.V(farmer).addE('GROWS').to(crop_node).property('land_acres', land_acres).iterate()
            
            conn.close()
            print(f"Added farmer {name} to Neptune graph")
            return True
            
        except Exception as e:
            print(f"Error adding to Neptune: {e}")
            return self._add_to_local_graph(profile)
    
    def _add_to_local_graph(self, profile: Dict) -> bool:
        """Add farmer to local in-memory graph (fallback)"""
        try:
            # Add farmer
            farmer_data = {
                "user_id": profile.get("user_id"),
                "name": profile.get("name"),
                "phone": profile.get("phone"),
                "village": profile.get("village"),
                "crops": profile.get("crops"),
                "land_acres": profile.get("land_acres"),
                "registered_at": profile.get("registered_at")
            }
            
            # Update if exists, else add
            existing = next((f for f in self.local_graph["farmers"] if f["user_id"] == farmer_data["user_id"]), None)
            if existing:
                self.local_graph["farmers"].remove(existing)
            self.local_graph["farmers"].append(farmer_data)
            
            # Add village if not exists
            village = profile.get("village")
            if village and village not in self.local_graph["villages"]:
                self.local_graph["villages"].append(village)
            
            # Add crops if not exists
            crops = profile.get("crops", "").split(",")
            for crop in crops:
                crop = crop.strip()
                if crop and crop not in self.local_graph["crops"]:
                    self.local_graph["crops"].append(crop)
            
            print(f"Added farmer {farmer_data['name']} to local graph")
            return True
            
        except Exception as e:
            print(f"Error adding to local graph: {e}")
            return False
    
    def get_village_farmers(self, village_name: str) -> List[Dict]:
        """Get all farmers in a village"""
        if self.use_neptune:
            return self._get_village_farmers_neptune(village_name)
        else:
            return [f for f in self.local_graph["farmers"] if f["village"] == village_name]
    
    def _get_village_farmers_neptune(self, village_name: str) -> List[Dict]:
        """Get village farmers from Neptune"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            g = traversal().withRemote(conn)
            
            # Query: Village -> LIVES_IN <- Farmer
            farmers = g.V().has('village', 'name', village_name).in_('LIVES_IN').valueMap(True).toList()
            
            conn.close()
            return farmers
            
        except Exception as e:
            print(f"Error querying Neptune: {e}")
            return []
    
    def get_crop_farmers(self, crop_name: str) -> List[Dict]:
        """Get all farmers growing a specific crop"""
        if self.use_neptune:
            return self._get_crop_farmers_neptune(crop_name)
        else:
            return [f for f in self.local_graph["farmers"] if crop_name in f.get("crops", "")]
    
    def _get_crop_farmers_neptune(self, crop_name: str) -> List[Dict]:
        """Get crop farmers from Neptune"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            g = traversal().withRemote(conn)
            
            # Query: Crop -> GROWS <- Farmer
            farmers = g.V().has('crop', 'name', crop_name).in_('GROWS').valueMap(True).toList()
            
            conn.close()
            return farmers
            
        except Exception as e:
            print(f"Error querying Neptune: {e}")
            return []
    
    def get_village_statistics(self, village_name: str) -> Dict:
        """Get statistics for a village"""
        farmers = self.get_village_farmers(village_name)
        
        if not farmers:
            return {"village": village_name, "farmer_count": 0}
        
        # Calculate statistics
        total_land = sum(float(f.get("land_acres", 0)) for f in farmers)
        crops = {}
        
        for farmer in farmers:
            farmer_crops = farmer.get("crops", "").split(",")
            for crop in farmer_crops:
                crop = crop.strip()
                if crop:
                    crops[crop] = crops.get(crop, 0) + 1
        
        return {
            "village": village_name,
            "farmer_count": len(farmers),
            "total_land_acres": total_land,
            "crops_grown": crops,
            "farmers": farmers
        }
    
    def get_all_villages(self) -> List[str]:
        """Get list of all villages"""
        if self.use_neptune:
            return self._get_all_villages_neptune()
        else:
            return self.local_graph["villages"]
    
    def _get_all_villages_neptune(self) -> List[str]:
        """Get all villages from Neptune"""
        try:
            conn = self.get_connection()
            if not conn:
                return []
            
            g = traversal().withRemote(conn)
            villages = g.V().hasLabel('village').values('name').toList()
            
            conn.close()
            return villages
            
        except Exception as e:
            print(f"Error querying Neptune: {e}")
            return []
    
    def get_graph_summary(self) -> Dict:
        """Get overall graph statistics"""
        if self.use_neptune:
            return self._get_graph_summary_neptune()
        else:
            return {
                "total_farmers": len(self.local_graph["farmers"]),
                "total_villages": len(self.local_graph["villages"]),
                "total_crops": len(self.local_graph["crops"]),
                "villages": self.local_graph["villages"],
                "crops": self.local_graph["crops"]
            }
    
    def _get_graph_summary_neptune(self) -> Dict:
        """Get graph summary from Neptune"""
        try:
            conn = self.get_connection()
            if not conn:
                return {}
            
            g = traversal().withRemote(conn)
            
            farmer_count = g.V().hasLabel('farmer').count().next()
            village_count = g.V().hasLabel('village').count().next()
            crop_count = g.V().hasLabel('crop').count().next()
            
            villages = g.V().hasLabel('village').values('name').toList()
            crops = g.V().hasLabel('crop').values('name').toList()
            
            conn.close()
            
            return {
                "total_farmers": farmer_count,
                "total_villages": village_count,
                "total_crops": crop_count,
                "villages": villages,
                "crops": crops
            }
            
        except Exception as e:
            print(f"Error querying Neptune: {e}")
            return {}
    
    def export_graph_data(self) -> Dict:
        """Export complete graph data for visualization"""
        if self.use_neptune:
            return self._export_neptune_data()
        else:
            return {
                "nodes": [
                    {"id": f["user_id"], "label": f["name"], "type": "farmer", "data": f}
                    for f in self.local_graph["farmers"]
                ] + [
                    {"id": f"village_{v}", "label": v, "type": "village"}
                    for v in self.local_graph["villages"]
                ] + [
                    {"id": f"crop_{c}", "label": c, "type": "crop"}
                    for c in self.local_graph["crops"]
                ],
                "edges": self._generate_local_edges()
            }
    
    def _generate_local_edges(self) -> List[Dict]:
        """Generate edges for local graph"""
        edges = []
        
        for farmer in self.local_graph["farmers"]:
            user_id = farmer["user_id"]
            village = farmer["village"]
            crops = farmer.get("crops", "").split(",")
            
            # Farmer -> Village
            edges.append({
                "source": user_id,
                "target": f"village_{village}",
                "label": "LIVES_IN"
            })
            
            # Farmer -> Crops
            for crop in crops:
                crop = crop.strip()
                if crop:
                    edges.append({
                        "source": user_id,
                        "target": f"crop_{crop}",
                        "label": "GROWS"
                    })
        
        return edges
    
    def _export_neptune_data(self) -> Dict:
        """Export Neptune graph data"""
        try:
            conn = self.get_connection()
            if not conn:
                return {"nodes": [], "edges": []}
            
            g = traversal().withRemote(conn)
            
            # Get all nodes
            farmers = g.V().hasLabel('farmer').valueMap(True).toList()
            villages = g.V().hasLabel('village').valueMap(True).toList()
            crops = g.V().hasLabel('crop').valueMap(True).toList()
            
            # Get all edges
            edges = g.E().project('source', 'target', 'label').by(__.outV().id()).by(__.inV().id()).by(__.label()).toList()
            
            conn.close()
            
            nodes = (
                [{"id": str(f['id']), "label": f.get('name', [''])[0], "type": "farmer", "data": f} for f in farmers] +
                [{"id": str(v['id']), "label": v.get('name', [''])[0], "type": "village"} for v in villages] +
                [{"id": str(c['id']), "label": c.get('name', [''])[0], "type": "crop"} for c in crops]
            )
            
            return {"nodes": nodes, "edges": edges}
            
        except Exception as e:
            print(f"Error exporting Neptune data: {e}")
            return {"nodes": [], "edges": []}


# Singleton instance
knowledge_graph = VillageKnowledgeGraph()
