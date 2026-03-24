from companie.models import Company

def company_info(request):
	company = Company.objects.first()
	return {
		'company':company
	}