def calculate_calories(
    age,
    gender,
    height,
    weight,
    activity,
    goal
):
    bmi = weight / ((height / 100) ** 2)
    
    if bmi < 18.5:
        bmi_status = "Underweight"
    elif bmi < 25:
        bmi_status = "Healthy Weight"
    elif bmi < 30:
        bmi_status = "Overweight"
    else:
        bmi_status = "Obese"
    
    if gender == 'male':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        
    maintenance = bmr * activity
    
    if goal == "weight_loss":
        target_calories = maintenance - 300
        recommendation = "Weight Loss"
    elif goal == "muscle_gain":
        target_calories = maintenance + 300 
    else:
        target_calories = maintenance
        recommendation = "Maintenance"
        
    return{
        'bmi': round(bmi,1),
        'bmr': round(bmr),
        'target_calories': round(target_calories),
        'recommendation': recommendation,
        'bmi_status': bmi_status,
    }