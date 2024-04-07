import abc
import glob
from dataclasses import dataclass

from jinja2 import Environment, FileSystemLoader, Template


@dataclass
class Recipe:
    title: str
    slug: str
    body: str
    rendered_body: str
    created_at: str


class RecipeRepository(abc.ABC):
    @abc.abstractmethod
    def find_all(self) -> list[Recipe]:
        raise NotImplementedError

    @abc.abstractmethod
    def find_by_slug(self, slug: str) -> Recipe | None:
        raise NotImplementedError


class MarkdownBody:
    def __init__(self, body: str) -> None:
        self.body = body

    def to_string(self) -> str:
        return self.body

    def get_images(self) -> list[str]:
        images = list()

        for line in self.body.splitlines():
            if '.png' not in line and '.jpg' not in line:
                continue

            extension_index = line.index('.png') or line.index('.jpg')

            current_index = extension_index - 1

            while True:
                current_char = line[current_index]

                if current_char.isalnum():
                    current_index -= 1
                else:
                    current_index += 1
                    break

            images.append(line[current_index:extension_index + 4])

        return list(set(images))


class HtmlBody:
    def __init__(self, body: str) -> None:
        self.body = body

    def to_string(self) -> str:
        return self.body


class FileSystemRecipeRepository:
    def __init__(self, content_root_dir: str):
        self._content_root_dir = content_root_dir
        self._content_root_dir = content_root_dir

    def load(self):
        recipe_files = glob.glob(self._content_root_dir + '/**/*.md')

        recipes_to_return = list()
        for recipe_file in recipe_files:
            markdown_body = self.read_recipe_file_content(recipe_file)
            recipe_title = self.extract_recipe_title(markdown_body.to_string())
            print(markdown_body.get_images())
            recipes_to_return.append(Recipe(title=recipe_title, slug=recipe_title, body=markdown_body.to_string(),
                                            rendered_body=markdown_body.to_string(), created_at='pizza'))

        return recipes_to_return

    @staticmethod
    def extract_recipe_title(markdown_body: str) -> str:
        for line in markdown_body.splitlines():
            if line[:2] == '# ':
                return line[2:].strip()

    @staticmethod
    def read_recipe_file_content(recipe_file_path: str) -> MarkdownBody:
        with open(recipe_file_path, 'r') as f:
            return MarkdownBody(f.read())

    def render_markdown_body(self, markdown_body: MarkdownBody) -> str:
        pass


@dataclass
class HTMLFile:
    filename: str
    content: str

    def get_filename(self) -> str:
        return self.filename + '.html'


@dataclass
class CompliedWebsite:
    html_files: list[HTMLFile]


class HTMLCompiler:
    def __init__(self):
        environment = Environment(loader=FileSystemLoader("templates/"))

        self._templates = environment
        # template = environment.get_template("message.txt")

    def _get_template(self, name: str) -> Template:
        return self._templates.get_template(name)

    def generate_html(self, recipes: list[Recipe]) -> CompliedWebsite:
        files = list()

        homepage_template = self._get_template('homepage.html')
        files.append(HTMLFile('homepage', homepage_template.render()))

        recipe_overview = self._get_template('recipe_overview.html')
        files.append(HTMLFile('recipe_overview', recipe_overview.render(recipies=recipes)))

        return CompliedWebsite(files)


class WebsiteRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, website: CompliedWebsite) -> None:
        raise NotImplementedError


class FileSystemWebsiteRepository(WebsiteRepository):
    def __init__(self, output_dir: str) -> None:
        self._output_dir = output_dir

    def save(self, website: CompliedWebsite) -> None:
        for html_file in website.html_files:
            with open(self._output_dir + '/' + html_file.get_filename(), 'w') as f:
                f.write(html_file.content)


if __name__ == '__main__':
    recipes = FileSystemRecipeRepository('/Users/matt/dev/cooking.mattiapeiretti.com/content').load()
    website = HTMLCompiler().generate_html(recipes)
    website_repo = FileSystemWebsiteRepository('/Users/matt/dev/cooking.mattiapeiretti.com/comp')
    website_repo.save(website)
