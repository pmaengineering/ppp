from jinja2 import Environment, FileSystemLoader, PackageLoader

def reference_material():
    def rotate_array(active):
        '''Rotate the entries of an array by a single position to the right'''
        # Remove the last element from the array
        element = active.pop()
        # Insert it as the first element of the array
        active.insert(0, element)

    # List of pages to be rendered -- MUST be listed according to their
    # order in the navigation bar
    # PAGE_LIST = ['index', 'research', 'projects', 'misc', 'contact',]
    PAGE_LIST = ['contact']

    # Title of individual pages
    TITLES = {
        'contact': 'Barun Saha | Contact',
        'index': 'Barun Saha',
        'misc': 'Barun Saha | Miscellaneous',
        'projects': 'Barun Saha | Projects',
        'research': 'Barun Saha | Research',
    }

    # CSS active class for the navigation bar list items
    state = ['active', '', '', '', '', '',]

    for item in PAGE_LIST:
        file_name = item + '.html'
        template = ENV.get_template(file_name)
        html = template.render(title=TITLES[item], active_state=state)

        # Write output in the corresponding HTML file
        print('Writing', file_name)
        with open(file_name, 'w') as out_file:
            out_file.write(html)

        # Rotate active states for the next page
        rotate_array(state)

# # # # # Everything above is just temporary reference material. # # # # #

def render_html(data):
    output_file = 'html_rendering_in_development.html'
    ENV = Environment(loader=PackageLoader('pmix'))
    template = ENV.get_template('base.html')
    # try:
    #     # try: os.path.join(os.path.split(__file__)[0], 'file')
    #     # Or try jinja2 package loader.
    #     ENV = Environment(loader=FileSystemLoader('./templates'))
    #     template = ENV.get_template('base.html')
    # except:
    #     ENV = Environment(loader=FileSystemLoader('./pmix/templates'))
    #     template = ENV.get_template('base.html')

    html = template.render(data=data)

    print('Writing: ', output_file)
    with open(output_file, 'w') as out_file:
        out_file.write(html)
