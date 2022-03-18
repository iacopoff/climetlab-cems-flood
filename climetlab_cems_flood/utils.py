from datetime import datetime, timedelta
import typing as T
import re

M = ["%02d"%d for  d in range(1,13)]
Y = [str(d) for d in range(2000,2019)]
D = ["%02d"%d for  d in range(1,32)]



class StringNotValidError(Exception):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def ensure_list(l):
    if isinstance(l,list):
        return l
    else:
        return [l]

def parser_time_index(start=[2019, 1, 1], end=[2019, 12, 31]):

    start, end = datetime(*start), datetime(*end)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    index = [
        list(map(str.lower, d.strftime("%B-%d").split("-")))
        for d in days
        if d.weekday() in [0, 3]
    ]

    return index


class Parser:

    def __init__(self,range_years=None):
        
        #TODO quite hacky
        if range_years:
            setattr(Parser,"Y",[str(d) for d in range(range_years[0],range_years[1]+1)])
        else:
            setattr(Parser,"Y",None)
        

    @staticmethod
    def leadtime(string, step):
        ret = []
        s = string.split("/")
        for chunk in s:
            if "-" in chunk:
                start, end = chunk.split("-")
                ret.extend(list(map(str, range(int(start), int(end) + step, step))))
            else:
                ret.append(chunk)

        return ret

    @classmethod
    def period(cls,string):

        
        PATTERN = {"[0-9]{8}":{}, # most frequent
                "\*[0-9]{2}[0-9]{2}":[cls.Y,string[1:3],string[3:]],
                "[0-9]{4}\*[0-9]{2}":[string[:4],M,string[5:]],
                "[0-9]{4}[0-9]{2}\*":[string[:4],string[1:3],D],
                "[0-9]{4}\*\*":[string[:4],M,D],
                "\*[0-9]{2}\*":[cls.Y,string[1:3],D],
                "\*\*[0-9]{2}":[cls.Y,M,string[3:]],
                "\*\*\*":[cls.Y,M,D],
                "\*[0-9-]{5}\*":[cls.Y,string[1:6],D],
                "[0-9-]{9}\*\*":[string[:9],M,D],
                "\*\*[0-9-]{5}":[cls.Y,M,string[3:]],

                "[0-9-]{9}[0-9-]{5}\*":[string[:9],string[9:14],D],
                "\*[0-9-]{5}[0-9-]{5}":[cls.Y, string[1:6],string[7:]]
                }

        #_validate(string)

        if "*" in string:
            years = set()
            months = set()
            days = set()     
            match = None
            for p in PATTERN:
                if re.match(p,string):
                    break
                
            years,months,days = list(map(unpack,PATTERN[p]))



            return sorted(ensure_list(years)), sorted(ensure_list(months)), sorted(ensure_list(days))

        s = string.split("/")

        years = set()
        months = set()
        days = set()
        for chunk in s:
            if "-" in chunk: # check "-"
                start, end = chunk.split("-")
                start = datetime.strptime(start, "%Y%m%d")
                end = datetime.strptime(end, "%Y%m%d")
                period = [
                    start + timedelta(days=x) for x in range(0, (end - start).days + 1)
                ]
                years.update([i.strftime("%Y") for i in period])
                months.update([i.strftime("%m") for i in period])
                days.update([i.strftime("%d") for i in period])
            else:
                years.update([chunk[:4]])
                months.update([chunk[4:6]])
                days.update([chunk[6:]])                 


        return sorted(list(years)), sorted(list(months)), sorted(list(days))



def _validate(string):
    if ("*" in string and "-" in string) or ("*" in string and "/" in string):
        raise StringNotValidError(string," '*' and '-' or '*' and '/' are not allowed in the same string")
    else:
        pass

def months_num2str(months: T.List[str]):
    mapping = {"01":"january","02":"february","03":"march","04":"april","05":"may",
               "06":"june","07":"july","08":"august","09":"september","10":"october",
              "11":"november","12":"december"}
    return [mapping.get(m) for m in months if mapping.get(m)]



def unpack(string):
    try:
        string.split("-")
        start, end = string.split("-")
        if len(start) <= 2:
            return ["%02d"%d for d in range(int(start),int(end)+1)]
        elif len(start) > 2:
            return [str(d) for d in range(int(start),int(end)+1)] 
    except:
        return string
    


def handle_cropping_area(request, area, lat, lon):

    if lat is not None and lon is not None:
        if area is not None:
            raise ValueError("Can't have ('lat' or 'lon') and 'area'")
        # Compute area from coordinates (MARS client)
        area = []
        lat, lon = list(map(ensure_list,[lat,lon]))
        for la,lo in zip(lat,lon):
            area.extend([la,lo,la,lo]) # N/W/S/E

    if isinstance(area, list):  
        request.update({"area":area})
    elif type(area).__name__ == 'GeoDataFrame' or type(area).__name__ == 'GeoSeries':
        W,S,E,N = area.unary_union.bounds # (minx, miny, maxx, maxy)
        bounds = [N,W,S,E]
        request.update({"area":bounds})


class ReprMixin:
    def _repr_html_(self):
        ret = super()._repr_html_()
    
        style = """
            <style>table.climetlab td {
            vertical-align: top;
            text-align: left !important;}
        </style>"""      
        
        li = ""
        for key in self.request:
            li += f"<li> <b>{key}: </b> {self.request[key]} </li>".format()
            
        return ret + f"""<table class="climetlab"><tr><td><b>Request</b></td><td><ul>{li}</ul></td></tr></table>"""