from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
def paginate(objects_list, request, per_page=10):
    try:
        per_page_val = int(request.GET.get('per_page', per_page))
        if per_page_val <= 0 or per_page_val > 100: per_page_val = per_page
    except (TypeError, ValueError):
        per_page_val = per_page

    paginator = Paginator(objects_list, per_page_val)
    page_number = request.GET.get('page', 1)

    try: page_obj = paginator.page(page_number)
    except PageNotAnInteger: page_obj = paginator.page(1)
    except EmptyPage: page_obj = paginator.page(paginator.num_pages)

    return page_obj
