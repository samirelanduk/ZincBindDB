from datetime import datetime
from unittest.mock import patch, Mock, MagicMock
from freezegun import freeze_time
from django.db import IntegrityError
from .base import ZincBindTest
from zincbind.factories import *

class EmptyPdbCreationTests(ZincBindTest):

    @freeze_time("2012-01-01 12:00:01")
    @patch("zincbind.factories.Pdb.objects.create")
    def test_can_add_empty_pdb(self, mock_create):
        create_empty_pdb("1ABC")
        mock_create.assert_called_with(id="1ABC", checked="2012-01-01 12:00:01")
