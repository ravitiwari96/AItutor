from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import AIChat
from .serializers import (
    AIChatSerializer,
    AIChatCreateSerializer
)
from .services import GeminiService
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_with_ai(request):
    """Chat with Gemini AI"""
    serializer = AIChatCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            gemini_service = GeminiService()
            
            if not gemini_service.is_configured():
                return Response(
                    {'error': 'AI chat service is not configured. Please contact administrator.'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            message = serializer.validated_data['message']
            result = gemini_service.generate_response(message)
            
            if result['success']:
                # Save chat to database only if user is authenticated
                chat = None
                if request.user.is_authenticated:
                    chat = AIChat.objects.create(
                        user=request.user,
                        message=message,
                        ai_response=result['response']
                    )
                    response_serializer = AIChatSerializer(chat)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    # For anonymous users, just return the response
                    return Response({
                        'message': message,
                        'ai_response': result['response'],
                        'created_at': None,
                        'user': None
                    }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': f'AI service error: {result["error"]}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error in chat_with_ai: {str(e)}")
            return Response(
                {'error': 'Failed to generate AI response. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def explain_concept(request):
    """Get AI explanation for a concept"""
    concept = request.data.get('concept', '').strip()
    difficulty = request.data.get('difficulty', 'intermediate')
    
    if not concept:
        return Response(
            {'error': 'Concept field is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        gemini_service = GeminiService()
        
        if not gemini_service.is_configured():
            return Response(
                {'error': 'AI service is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        result = gemini_service.explain_concept(concept, difficulty)
        
        if result['success']:
            # Save as chat only if user is authenticated
            chat_id = None
            if request.user.is_authenticated:
                chat = AIChat.objects.create(
                    user=request.user,
                    message=f"Explain concept: {concept} (difficulty: {difficulty})",
                    ai_response=result['response']
                )
                chat_id = chat.id
            
            return Response({
                'concept': concept,
                'difficulty': difficulty,
                'explanation': result['response'],
                'chat_id': chat_id
            })
        else:
            return Response(
                {'error': f'AI service error: {result["error"]}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in explain_concept: {str(e)}")
        return Response(
            {'error': 'Failed to generate explanation.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def generate_educational_content(request):
    """Generate educational content for a topic"""
    topic = request.data.get('topic', '').strip()
    grade_level = request.data.get('grade_level', 'general')
    
    if not topic:
        return Response(
            {'error': 'Topic field is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        gemini_service = GeminiService()
        
        if not gemini_service.is_configured():
            return Response(
                {'error': 'AI service is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        result = gemini_service.generate_educational_content(topic, grade_level)
        
        if result['success']:
            # Save as chat only if user is authenticated
            chat_id = None
            if request.user.is_authenticated:
                chat = AIChat.objects.create(
                    user=request.user,
                    message=f"Generate educational content for: {topic} (grade: {grade_level})",
                    ai_response=result['response']
                )
                chat_id = chat.id
            
            return Response({
                'topic': topic,
                'grade_level': grade_level,
                'content': result['response'],
                'chat_id': chat_id
            })
        else:
            return Response(
                {'error': f'AI service error: {result["error"]}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in generate_educational_content: {str(e)}")
        return Response(
            {'error': 'Failed to generate educational content.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_chats(request):
    """List user's AI chats - requires authentication"""
    try:
        chats = AIChat.objects.filter(user=request.user)[:20]  # Last 20 chats
        serializer = AIChatSerializer(chats, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Error listing user chats: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve chats.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 

@api_view(['GET']) 
@permission_classes([AllowAny])
def api_status(request):
    """Check API services status"""
    try:
        from .services import GeminiService
        
        gemini_service = GeminiService()
        
        # Test Gemini configuration
        gemini_configured = bool(gemini_service.api_key and gemini_service.model)
        
        return Response({
            'gemini': {
                'configured': gemini_configured,
                'connected': gemini_configured,
                'model': 'gemini-1.5-flash'
            }
        })

    except Exception as e:
        logger.error(f"Error checking API status: {str(e)}")
        return Response(
            {'error': 'Failed to check API status.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def service_status(request):
    """Check AI service status"""
    try:
        gemini_service = GeminiService()
        
        # Test Gemini configuration
        gemini_configured = gemini_service.is_configured()
        
        return Response({
            'gemini': {
                'configured': gemini_configured,
                'service': 'Google Gemini AI'
            }
        })

    except Exception as e:
        logger.error(f"Error checking service status: {str(e)}")
        return Response(
            {'error': 'Failed to check service status.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )