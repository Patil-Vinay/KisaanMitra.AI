"""
Monitoring Service - Health checks and performance monitoring
"""
import time
import json
from datetime import datetime


class HealthCheckService:
    """Health check endpoints and system monitoring"""
    
    @staticmethod
    def check_system_health():
        """Comprehensive system health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {},
            "performance": {}
        }
        
        # Check AI Service
        try:
            from services.ai_service import bedrock
            if bedrock:
                health_status["checks"]["ai_service"] = "healthy"
            else:
                health_status["checks"]["ai_service"] = "unhealthy"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["ai_service"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check WhatsApp Service
        try:
            import os
            whatsapp_token = os.environ.get("WHATSAPP_TOKEN")
            phone_id = os.environ.get("PHONE_NUMBER_ID")
            
            if whatsapp_token and phone_id:
                health_status["checks"]["whatsapp_service"] = "healthy"
            else:
                health_status["checks"]["whatsapp_service"] = "misconfigured"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["whatsapp_service"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
        
        # Check DynamoDB connectivity
        try:
            import boto3
            dynamodb = boto3.resource("dynamodb", region_name="ap-south-1")
            table = dynamodb.Table("kisaanmitra-conversations")
            
            # Simple connectivity test
            table.table_status
            health_status["checks"]["dynamodb"] = "healthy"
        except Exception as e:
            health_status["checks"]["dynamodb"] = f"error: {str(e)}"
            health_status["status"] = "unhealthy"
        
        # Check Cache Service
        try:
            from services.cache_service import CacheService
            cache_stats = CacheService.get_stats()
            health_status["checks"]["cache_service"] = "healthy"
            health_status["performance"]["cache"] = cache_stats
        except Exception as e:
            health_status["checks"]["cache_service"] = f"error: {str(e)}"
        
        # Check Market Data API
        try:
            api_key = os.environ.get("AGMARKNET_API_KEY")
            if api_key and api_key != "not_available":
                health_status["checks"]["agmarknet_api"] = "configured"
            else:
                health_status["checks"]["agmarknet_api"] = "not_configured"
        except Exception as e:
            health_status["checks"]["agmarknet_api"] = f"error: {str(e)}"
        
        return health_status
    
    @staticmethod
    def get_performance_metrics():
        """Get system performance metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "memory": {},
            "cache": {},
            "api_calls": {}
        }
        
        # Memory usage (approximate)
        try:
            import psutil
            process = psutil.Process()
            metrics["memory"] = {
                "rss_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "vms_mb": round(process.memory_info().vms / 1024 / 1024, 2)
            }
        except:
            metrics["memory"] = {"status": "unavailable"}
        
        # Cache statistics
        try:
            from services.cache_service import CacheService
            metrics["cache"] = CacheService.get_stats()
        except:
            metrics["cache"] = {"status": "unavailable"}
        
        return metrics


class PerformanceMonitor:
    """Performance monitoring and optimization suggestions"""
    
    _metrics = {
        "request_count": 0,
        "total_response_time": 0,
        "error_count": 0,
        "cache_hits": 0,
        "cache_misses": 0
    }
    
    @classmethod
    def record_request(cls, response_time_ms, success=True):
        """Record request metrics"""
        cls._metrics["request_count"] += 1
        cls._metrics["total_response_time"] += response_time_ms
        
        if not success:
            cls._metrics["error_count"] += 1
    
    @classmethod
    def record_cache_hit(cls):
        """Record cache hit"""
        cls._metrics["cache_hits"] += 1
    
    @classmethod
    def record_cache_miss(cls):
        """Record cache miss"""
        cls._metrics["cache_misses"] += 1
    
    @classmethod
    def get_metrics(cls):
        """Get performance metrics"""
        total_requests = cls._metrics["request_count"]
        
        if total_requests == 0:
            return {
                "status": "no_data",
                "message": "No requests recorded yet"
            }
        
        avg_response_time = cls._metrics["total_response_time"] / total_requests
        error_rate = (cls._metrics["error_count"] / total_requests) * 100
        
        total_cache_requests = cls._metrics["cache_hits"] + cls._metrics["cache_misses"]
        cache_hit_rate = (cls._metrics["cache_hits"] / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "error_rate_percent": round(error_rate, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "recommendations": cls._get_recommendations(avg_response_time, error_rate, cache_hit_rate)
        }
    
    @classmethod
    def _get_recommendations(cls, avg_response_time, error_rate, cache_hit_rate):
        """Generate performance recommendations"""
        recommendations = []
        
        if avg_response_time > 5000:  # 5 seconds
            recommendations.append("High response time detected. Consider optimizing AI calls or increasing Lambda memory.")
        
        if error_rate > 5:  # 5%
            recommendations.append("High error rate detected. Check logs for recurring issues.")
        
        if cache_hit_rate < 30:  # Less than 30%
            recommendations.append("Low cache hit rate. Consider increasing cache TTL or improving cache key strategy.")
        
        if not recommendations:
            recommendations.append("System performance is within acceptable ranges.")
        
        return recommendations
    
    @classmethod
    def reset_metrics(cls):
        """Reset all metrics"""
        cls._metrics = {
            "request_count": 0,
            "total_response_time": 0,
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }


def create_health_check_handler():
    """Create a health check handler for API Gateway"""
    def health_check_handler(event, context):
        """Lambda handler for health checks"""
        try:
            # Check if this is a health check request
            path = event.get("path", "")
            
            if path == "/health":
                health_status = HealthCheckService.check_system_health()
                
                status_code = 200
                if health_status["status"] == "unhealthy":
                    status_code = 503
                elif health_status["status"] == "degraded":
                    status_code = 200  # Still functional
                
                return {
                    'statusCode': status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(health_status, indent=2)
                }
            
            elif path == "/metrics":
                metrics = PerformanceMonitor.get_metrics()
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps(metrics, indent=2)
                }
            
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({"error": "Not found"})
                }
                
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps({"error": str(e)})
            }
    
    return health_check_handler