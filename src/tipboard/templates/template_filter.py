from django import template
from django.template.loader import render_to_string
from src.tipboard.app.properties import ALLOWED_TILES

register = template.Library()


def isTxt_tile(tile_template):
    return tile_template in ['text', 'simple_percentage', 'big_value', 'listing', 'just_value']


def isChartJS_tile(tile_template):
    return tile_template in ['bar_chart', 'vbar_chart',
                             'pie_chart', 'polararea_chart', 'radar_chart',
                             'doughnut_chart', 'half_doughnut_chart',
                             'gauge_chart', 'radial_gauge_chart', 'linear_gauge_chart', 'vlinear_gauge_chart',
                             'line_chart', 'cumulative_flow', 'norm_chart']


@register.filter(name='template_tile_dashboard')
def template_tile_dashboard(tile_id, layout_name):
    """
        Many thanks to for the solution for multiple argument in template html django
        For detail, see Stackoverflow answer: https://stackoverflow.com/a/24402622/4797299
    """
    return tile_id, layout_name


def handle_errors(tile_data, templateData, isTemplateNotFound=False):
    if not isinstance(tile_data, dict):
        templateData['reason'] = 'data for tile is incorrect'
    elif tile_data['tile_template'] not in ALLOWED_TILES:
        templateData['reason'] = 'tile template is not allowed'
    elif isTemplateNotFound:
        templateData['reason'] = 'not found'
    return render_to_string(f'tiles/notfound_tiles.html', templateData)


def get_name_of_template(tile_data):
    name_of_template = f'tiles/{tile_data["tile_template"]}.html'
    if isChartJS_tile(tile_data['tile_template']):
        name_of_template = f'tiles/chartJS_template.html'
    elif isTxt_tile(tile_data['tile_template']):
        name_of_template = f'tiles/txt_{tile_data["tile_template"]}.html'
    return name_of_template


@register.filter(name='template_tile_data')
def template_tile_data(packedData, data):
    """
     this is the template to string render, of the tiles template in config.yaml
    :param packedData: (id of title
    :param data: data to be send to the template tile
    :return: a string, representing the html generated by the tile template
    """
    template_data = dict(tile_id='ID_NOT_FOUND', tile_template='TEMPLATE_NOT_FOUND')
    if isinstance(data, dict) and data['tile_template'] in ALLOWED_TILES:
        try:
            tile_id, layout_name = packedData
            template_data['tile_id'] = f'{layout_name}-{tile_id}'
            template_data['tile_template'] = data['tile_template']
            template_data['title'] = data['title'] if 'title' in data else 'TITLE_NOT_FOUND'
            return render_to_string(get_name_of_template(tile_data=data), template_data)
        except Exception:
            pass
    return handle_errors(data, template_data, False)
