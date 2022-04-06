
import re

from aiohttp import web

class Element:
    """ base class for a node in the widget tree """
    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.parent = None

    def render(self):
        """ returns a str of the html that encodes this element (and child elements).
            Put the elements javascript inline with the html
        """
        pass

    def add_child(self, child):
        """ adds a child element in the element tree """
        self.nodes.append(child)
        child.parent = self

    @property
    def top(self):
        node = self
        while node != None:
            node = self.parent
        return node

    @staticmethod
    def load_template(filename):
        with open(filename, 'r') as file:
            return file.read()

    @staticmethod
    def format(pre_format, **kwargs):
        """ poor mans html template system. {{var}} in the template can be over written with kwargs[var]"""

        # swaps double and single curly braces allowing us to use python str.format() method
        curly = { "{{":"{", "}}":"}", "{":"{{", "}":"}}" }
        substrings = sorted(curly, key=len, reverse=True)
        regex = re.compile('|'.join(map(re.escape, substrings)))
        to_formant = regex.sub(lambda match: curly[match.group(0)], pre_format)

        return to_formant.format(**kwargs) 

    ## OLD
    def get_identifier(self):
        """ generates a unique (but consistent) id that can be used in client - server communication """
        if self.identifier is not None:
            return self.identifier
        if self.parent is None:
            self.identifier = self.name
        else:
            self.identifier = self.parent.get_identifier() + "." + self.name
            # we assume an element's name is unique among siblings

        return self.identifier


class Graph(Element):
    pass

class RawSensorTable(Element):

    def __init__(self, name, line_ids):
        super().__init__(name)
        self.line_ids = line_ids

    def render(self):
        main = """
    <table class="dashboard-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>PIN</th>
          <th>Desc</th>
          <th>Value</th>
          <th>Units</th>
        </tr>
      </thead>
      <tbody>
        {{content}}
      </tbody>
    </table>

    <script>
    new_data_callbacks.push( () => { 
    {{update_code}}
    });
    </script>
"""

        line_template = """
        <tr>
          <td>{{id}}</td>
          <td>{{desc}}</td>
          <td>{{pin}}</td>
          <td> <p id={{id}}> None </p> </td>
          <td>{{unit}}</td>
        </tr>
"""

        lines = []
        update_code = []
        for id in self.line_ids:
            lines.append( line_template.format(id=id, 
                                 desc=self.get_meta(id, "desc"),
                                 pin=self.get_meta(id, "pin"),
                                 unit=self.get_meta(id, "unit") ))

            update_code.append( f"document.getElementById(id).innerHTML = get_data({id})" )

        return self.format(main, content = "\n".join(lines), update_code="\n".join(update_code))


class Page(Element):

    def __init__(self, name, parent):
        super().__init__(name)
        self.parent = parent

    def render(self):
        pass

    def add_routes(self):
        pass

    async def get_page(self, request):
        print("getting")
        return web.Response(text=self.render(), content_type='text/html')


class Dashboard(Page):

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.add_routes()

        self.add_child(
            RawSensorTable("Sensors", ["slate.press.ox_fill",
                                       "slate.press.ox_vent"]
            )
        )

    def render(self):
        dashboard = self.load_template("templates/dashboard.template.html")
        template = self.load_template("templates/main.template.html")

        dashboard_done = self.format(dashboard, content = "\n\n".join(child.render for child in self.nodes))
        return self.format(template, page = dashboard_done)


    def add_routes(self):
        print("hi")
        self.top.app.router.add_get('/', self.get_page)
        self.top.app.router.add_get('/dashboard', self.get_page)


class Messages(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        messages = self.load_template("templates/messages.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = messages)

class Maps(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        map = self.load_template("templates/map.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = map)

class Graphs(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        graphs = self.load_template("templates/graphs.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = graphs)

class Configure(Element):
    # def __init__(self):
    #     super().__init__(self.name)

    def render(self):
        # identifier = self.get_identifier()
        # content = "\n".join(child.render() for child in self.nodes)
        configure = self.load_template("templates/configure.template.html")
        template = self.load_template("templates/main.template.html")

        return self.format(template, page = configure)