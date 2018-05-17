from .base import FunctionalTest

class HomePageTests(FunctionalTest):

    def test_home_page_layout(self):
        self.get("/")
        self.check_title("ZincBind")
