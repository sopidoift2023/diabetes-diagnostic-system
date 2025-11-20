# diabetes_app/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .model_loader import diabetes_model
from django.core.cache import cache
from django.http import JsonResponse
from .models import PredictionLog
from django.utils.timezone import now
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile
from .models import UserPredictionHistory
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def index(request):
    """Home page view"""
    return render(request, 'diabetes_app/index.html')


def predict_view(request):
    """Prediction form view"""
    return render(request, 'diabetes_app/predict.html')


def results(request):
    """Results display view"""
    # Get prediction results from session or redirect to form
    prediction_result = request.session.get('prediction_result', None)
    if not prediction_result:
        return redirect('predict')

    return render(request, 'diabetes_app/results.html', {
        'prediction': prediction_result
    })

@csrf_exempt
def handle_prediction(request):
    """Handle form submission and display results"""
    if request.method == 'POST':
        try:
            # Get form data
            form_data = {
                'gender': request.POST.get('gender', ''),
                'age': float(request.POST.get('age', 0)),
                'hypertension': int(request.POST.get('hypertension', 0)),
                'heart_disease': int(request.POST.get('heart_disease', 0)),
                'smoking_history': request.POST.get('smoking_history', ''),
                'bmi': float(request.POST.get('bmi', 0)),
                'blood_glucose_level': float(request.POST.get('blood_glucose_level', 0))
            }

            # Validate required fields
            required_fields = ['gender', 'smoking_history']
            for field in required_fields:
                if not form_data[field]:
                    return render(request, 'diabetes_app/predict.html', {
                        'error': f'Missing required field: {field}',
                        'form_data': form_data
                    })

            # Make prediction
            result = diabetes_model.predict_diabetes(form_data)

            if 'error' in result:
                return render(request, 'diabetes_app/predict.html', {
                    'error': result['error'],
                    'form_data': form_data
                })

            # Log the prediction to database
            prediction_log = PredictionLog.objects.create(
                gender=form_data['gender'],
                age=form_data['age'],
                hypertension=bool(form_data['hypertension']),
                heart_disease=bool(form_data['heart_disease']),
                smoking_history=form_data['smoking_history'],
                bmi=form_data['bmi'],
                glucose_level=form_data['blood_glucose_level'],
                prediction=bool(result['diabetes_prediction']),
                probability_no_diabetes=result['probability_no_diabetes'],
                probability_diabetes=result['probability_diabetes'],
                confidence=result['confidence'],
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )

            # --- NEW CODE: LINK PREDICTION TO USER ---
            if request.user.is_authenticated:
                # Create a link between the user and this prediction
                UserPredictionHistory.objects.create(
                    user=request.user,
                    prediction=prediction_log
                )
            # --- END NEW CODE ---

            # Store result in session and redirect to results page
            request.session['prediction_result'] = result
            return redirect('results')

        except ValueError as e:
            return render(request, 'diabetes_app/predict.html', {
                'error': 'Please enter valid numbers for age, BMI, and glucose level',
                'form_data': request.POST.dict()
            })
        except Exception as e:
            return render(request, 'diabetes_app/predict.html', {
                'error': f'An error occurred: {str(e)}',
                'form_data': request.POST.dict()
            })

    return redirect('predict')

@csrf_exempt
@require_http_methods(["POST"])
def predict_api(request):
    """API endpoint for diabetes prediction"""
    try:
        data = json.loads(request.body.decode('utf-8'))

        input_data = {
            'gender': str(data.get('gender', '')),
            'age': float(data.get('age', 0)),
            'hypertension': int(data.get('hypertension', 0)),
            'heart_disease': int(data.get('heart_disease', 0)),
            'smoking_history': str(data.get('smoking_history', '')),
            'bmi': float(data.get('bmi', 0)),
            'blood_glucose_level': float(data.get('blood_glucose_level', 0))
        }

        result = diabetes_model.predict_diabetes(input_data)

        if 'error' in result:
            return JsonResponse({
                'success': False,
                'error': result['error']
            }, status=500)

        return JsonResponse({
            'success': True,
            'result': result
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'model_loaded': diabetes_model.model_loaded,
        'message': 'Diabetes prediction API is running'
    })



def predict_api(request):
    # Rate limiting: 10 requests per minute per IP
    ip = request.META.get('REMOTE_ADDR')
    key = f"rate_limit_{ip}"
    count = cache.get(key, 0)

    if count >= 10:
        return JsonResponse({
            'success': False,
            'error': 'Rate limit exceeded. Please try again in a minute.'
        }, status=429)

    cache.set(key, count + 1, 60)  # 60 seconds expiration


# --- NEW AUTHENTICATION VIEWS ---

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after registration
            login(request, user)
            return redirect('index')  # Redirect to home page after registration
    else:
        form = UserCreationForm()

    return render(request, 'diabetes_app/register.html', {'form': form})


@login_required
@login_required
def prediction_history(request):
    """View to show only the current user's prediction history"""
    # Get all predictions linked to this user through UserPredictionHistory
    user_predictions = PredictionLog.objects.filter(
        userpredictionhistory__user=request.user
    ).order_by('-timestamp')

    # Debug: Print how many predictions were found
    print(f"Found {user_predictions.count()} predictions for user {request.user.username}")

    return render(request, 'diabetes_app/history.html', {
        'predictions': user_predictions,
        'message': 'Your personal prediction history'
    })