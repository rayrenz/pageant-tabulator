import json
from io import BytesIO
from reportlab.pdfgen import canvas
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.generic import View, ListView
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.middleware.csrf import _get_new_csrf_string
from braces.views import JSONResponseMixin
from .models import Category, Candidate, Score, User, Talent, Final
from easy_pdf.views import PDFTemplateView

# Create your views here.
class IndexView(View):
    def get(self, request, *args, **kwargs):
        response = render(request, 'index.html')
        response.set_cookie('csrftoken', _get_new_csrf_string())
        return response


class Authentication(View):
    def get(self, request, *args, **kwargs):
        context = {
            'authenticated': request.user.is_authenticated,
            'user': request.user.username,
            'role': request.user.role if request.user.is_authenticated else ''
        }
        return HttpResponse(json.dumps(context), content_type='application/json')


class LoginView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user is not None and user.is_authenticated:
            login(request, user)
            context = {
                'authenticated': request.user.is_authenticated,
                'user': request.user.username,
                'role': request.user.role if request.user.is_authenticated else ''
            }
        else:
            context = {
                'authenticated': False
            }
        return HttpResponse(json.dumps(context), content_type='application/json')


class TemplateView(View):

    def get(self, request, *args, **kwargs):
        if request.is_ajax:
            name = kwargs.get('name')
            return render(request, name)
        raise Http404


class LogoutView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(LogoutView, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        logout(request)
        context = {
            'authenticated': request.user.is_authenticated
        }
        return HttpResponse(json.dumps(context), content_type='application/json')


def get_json(queryset, fields=None):
    dataset = []
    for obj in queryset:
        item = {}
        fields = fields if fields else [f.name for f in obj._meta.fields]
        for field in fields:
            value = getattr(obj, field)
            if type(value) in [bool, float]:
                item[field] = value
            else:
                item[field] = str(value)
        dataset.append(item)
    return dataset


def get_scores(request, category):
    if request.user.is_authenticated and request.user.role == 'j':
        scores = Score.objects.filter(category__name=category, judge=request.user)
    else:
        scores = Score.objects.filter(category__name=category)
    scores = get_json(scores, ['candidate', 'points', 'judge'])
    return HttpResponse(json.dumps(scores), content_type='application/json')


class CategoriesView(JSONResponseMixin, View):
    def get(self, *args, **kwargs):
        categories = Category.objects.all()
        return self.render_json_response(get_json(categories))

class CandidatesView(JSONResponseMixin, View):
    def get(self, *args, **kwargs):
        candidates = Candidate.objects.all()
        return self.render_json_response(get_json(candidates))


class ScoresView(JSONResponseMixin, View):
    def get(self, request, *args, **kwargs):
        category = kwargs.get('category', '')
        judge = request.user if request.user.role == 'j' else None
        if judge:
            scores = Score.objects.filter(judge=judge, category__name=category)
        else:
            scores = Score.objects.filter(category__name=category)
        scores = get_json(scores)
        return self.render_json_response(scores)

    def post(self, request, *args, **kwargs):
        category = kwargs.get('category', '')
        category = Category.objects.get(name=category)
        scores = json.loads(request.body.decode('utf-8'))
        if category.readonly:
            return self.render_json_response({'message': 'Saving failed: This event is closed.', 'type': 'error'})
        if len(list(scores.keys())) < 1:
            return self.render_json_response({'message': 'No new scores were saved.', 'type': 'error'})
        for id, points in scores.items():
            if not points: continue
            candidate = Candidate.objects.get(id=id)
            x = Score.objects.filter(category=category, candidate=candidate, judge=request.user)
            if x.__len__() > 0:
                x[0].points = points
                x[0].save()
            else:
                x = Score.objects.create(category=category, candidate=candidate, judge=request.user, points=points)
        return self.render_json_response({'message': 'Saved successfully. You can still update the scores.', 'type': 'success'})


class JudgeScoresView(JSONResponseMixin, View):
    def get(self, *args, **kwargs):
        category = kwargs.get('category', '')
        judges = get_json(User.objects.filter(role='j'), ['username'])
        for judge in judges:
            scores = get_json(Score.objects.filter(judge__username=judge['username'], category__name=category))
            judge['scores'] = scores
        return self.render_json_response(judges)

def add(a, b):
    a += b
    return a


class CategoryResultsView(PDFTemplateView, JSONResponseMixin, View):
    template_name = 'category-results.html'
    def get(self, *args, **kwargs):
        category = kwargs.get('category')
        format = kwargs.get('format')
        if not category or not format:
            raise Http404
        candidates = get_json(Candidate.objects.all())
        averages = []
        judges = get_json(User.objects.filter(role='j'), ['username'])
        for candidate in candidates:
            scores = get_json(Score.objects.filter(candidate__id=candidate.get('id'), category__name=category))
            total = 0
            candidate['scores'] = []
            score_count = 0
            for score in scores:
                score_count += 1
                total += score.get('points', 0)
            candidate['scores'] = scores
            for judge in judges:
                has_score = False
                for score in scores:
                    if judge.get('username') in [x for x in list(score.values())]:
                        has_score = True
                        break
                if not has_score:
                    candidate['scores'].append({'judge': judge.get('username'), 'points': ''})
            if score_count > 0:
                average = float('{0:.2f}'.format(total / score_count))
                candidate['average'] = average
                averages.append((candidate.get('average'), candidate.get('id')))
                candidate['total'] = total

        prev = None
        rank = 1
        for average, id in sorted(averages, reverse=True):
            for candidate in candidates:
                if candidate.get('id') == id:
                    if prev is None: prev = average
                    if prev > average: rank += 1
                    candidate['rank'] = rank
                    prev = average
        context = {
            'candidates': candidates,
            'judges': judges,
            'category': Category.objects.get(name=category).title
        }
        if format == 'json':
            return self.render_json_response(context)
        elif format == 'pdf':
            return self.render_to_response(context)


class TopSevenView(PDFTemplateView, JSONResponseMixin, View):
    template_name = 'top-seven.html'

    def get(self, *args, **kwargs):
        format = kwargs.get('format')
        context = {}
        candidates = Candidate.objects.all()
        categories = Category.objects.all()
        candidates_dict = get_json(candidates)
        categories_dict = get_json(categories)
        for candidate in candidates_dict:
            candidate['total'] = 0
            for cat in categories_dict:
                scores = Score.objects.filter(candidate__id=candidate.get('id'), category__name=cat.get('name'), )
                total = 0
                for score in scores:
                    total += score.points
                if total > 0:
                    average = float("{0:.2f}".format(total / len(scores)))
                    candidate[cat.get('name')] = {
                        'average': average,
                        'weight': float('{0:.2f}'.format(average * cat.get('weight')))
                    }
                candidate['total'] += candidate.get(cat.get('name'), {}).get('weight', 0)

            talent = Talent.objects.filter(candidate__id=candidate.get('id'))
            if talent.__len__() > 0:
                candidate['talent'] = {
                    'average': talent[0].points,
                    'weight': float('{0:.2f}'.format(talent[0].points * talent[0].weight))
                }
                candidate['total'] += candidate.get('talent', {}).get('weight', 0)

            candidate['total'] = float('{0:.2f}'.format(candidate['total']))


        #ranking
        totals = []
        for candidate in candidates_dict:
            total = candidate.get('total', 0)
            if total:
                totals.append((total, candidate.get('id')))
        rank = 1
        prev = None
        for total, id in sorted(totals, reverse=True):
            if prev is None: prev = total
            for candidate in candidates_dict:
                if candidate.get('id') == id:
                    if prev > total:
                        rank += 1
                    candidate['rank'] = rank
                    prev = total

        context['candidates'] = candidates_dict
        if format == 'json':
            return self.render_json_response(context)
        else:
            return self.render_to_response(context)


class FinalView(JSONResponseMixin, View):
    def get(self, *args, **kwargs):
        j = self.request.user
        final = get_json(Final.objects.filter(judge=j))
        return self.render_json_response(final)

    def post(self, *args, **kwargs):
        scores = json.loads(self.request.body.decode('utf-8'))
        judge = self.request.user
        test = []
        for id, rank in scores.items():
            test.append((rank, id))
        test2 = {}
        for x, y in test:
            test2[x] = []
        for x, y in test:
            test2[x].append(y)
        for key, val in test2.items():
            if len(val) > 1:
                return self.render_json_response({'message': 'Duplicate ranks', 'type': 'error'})
        Final.objects.filter(judge=judge).delete()
        for id, rank in scores.items():
            if not rank: continue
            candidate = Candidate.objects.get(id=id)
            final = Final.objects.create(candidate=candidate, judge=judge, rank=rank)
            final.save()
        return self.render_json_response({'message': 'Saved successfully.', 'type': 'success'})


class FinalResultsView(PDFTemplateView, JSONResponseMixin, View):
    template_name = 'final-result.html'
    def get(self, *args, **kwargs):
        format = kwargs.get('format')
        final = Final.objects.all()
        candidates = get_json(Candidate.objects.filter(finalist=True))
        judges = get_json(User.objects.filter(role='j'), ['username'])
        ranks = []
        for candidate in candidates:
            id = candidate.get('id')
            myranks = get_json(final.filter(candidate__id=id), ['judge', 'rank'])
            candidate['ranks'] = [[x.get('judge'), x.get('rank')] for x in myranks]
            total = 0
            for rank in myranks:
                total += rank.get('rank', 0)
            if len(candidate['ranks']) > 0:
                candidate['total'] = total
                ranks.append((total, candidate.get('id')))
            for judge in judges:
                has_rank = False
                for rank in myranks:
                    if rank.get('judge') == judge.get('username'):
                        has_rank = True
                if not has_rank:
                    candidate['ranks'].append([judge.get('username'), ''])
            candidate['ranks'] = sorted(candidate['ranks'])
        print(ranks)
        prev = None
        final_rank = 1
        for rank, id in sorted(ranks):
            if prev is None: prev = rank
            for candidate in candidates:
                if candidate.get('id') == id:
                    if prev < rank: final_rank += 1
                    candidate['final_rank'] = final_rank
                    prev = rank

        context = {
            'candidates': candidates,
            'judges': judges
        }
        if format == 'json':
            return self.render_json_response(context)
        else:
            return self.render_to_response(context)
