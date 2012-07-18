def dist_metric(function):
    def _inner(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (ValueError, TypeError):
            return None
    return _inner

### Distance metrics ##########################################################

@dist_metric
def nominal(a,b):
    return a != b

#@dist_metric
#def ordinal(a,b):
#    return a != b

@dist_metric
def interval(a,b):
    return (a-b)**2

@dist_metric
def ratio(a,b):
    return ((a-b)/(a+b))**2
    

#! This is not the greatest validtor.  Works for now.
def valid_value(a):
    try:
        float(a)
        return 1
    except (ValueError, TypeError):
        return 0

def drop_empty_values(data):
    for i,doc in enumerate(data):
        new_doc = []
        for value in doc: #!Remove all invalid values
            if valid_value(value):
                new_doc.append(value)
        data[i] = new_doc
    return data

def alpha(data, metric=nominal):
    data = drop_empty_values(data)
    
#    print data
    n = 0.
    for doc in data:
        if len(doc) > 1:
            n += len(doc)

    if n == 0:
        return None
    
    De = 0.
    for doc_1 in data:
        for doc_2 in data:
            if len(doc_1) > 1 and len(doc_2) > 1:
                De += sum(metric(code_a, code_b) for code_a in doc_1 for code_b in doc_2)
    De /= float(n*(n-1))

    if De == 0:
        return None

    Do = 0.
    for doc in data:
        if len(doc) > 1:
            D_doc = sum(metric(code_a, code_b) for code_a in doc for code_b in doc)
            Do += D_doc/float(len(doc)-1)
    Do /= float(n)

#    print '.'*80
#    print n
#    print Do
#    print De
#    print 1.-Do/De

    return 1.-Do/De


if __name__ == '__main__': 
    #Wikipedia example:
    array = [[1], [2,2],[1,1],[3,3],[3,3,4],[4,4,4],[1,3],[2,2],[1,1],[1,1],[3,3],[3,3],[],[3,4]]
    print "nominal alpha: %.4f" % alpha(array,nominal)
    print "ordinal alpha: %.4f" % alpha(array,ordinal)
    print "interval alpha: %.4f" % alpha(array,interval)

    assert alpha( [[1], [2,2],[1,1],[3,3],[3,3,4],[4,4,4],[1,3],[2,2],[1,1],[1,1],[3,3],[3,3],[],[3,4]], nominal ) == 0.691358024691
    assert alpha( [[1], [2,2],[1,1],[3,3],[3,3,4],[4,4,4],[1,3],[2,2],[1,1],[1,1],[3,3],[3,3],[],[3,4]], interval ) == 0.691358024691
    assert alpha( [[2,2],[1,1],[3,3]], nominal ) == 1
    assert alpha( [[2,2],[1,1],[3,3]], interval ) == 1
