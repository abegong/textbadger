from django import template
register = template.Library()
 
@register.filter(&quot;mongo_id&quot;)
def mongo_id(value):
   
    # Retrieve _id value
    if type(value) == type({}):
        if value.has_key('_id'):
            value = value['_id']
   
    # Return value
    return unicode(value)
