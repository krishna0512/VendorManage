from django.urls import reverse
from django.test.utils import setup_test_environment
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save

# from benchmark.forms import *
# import requests
import os
# from nltk.corpus import stopwords
import sys
import random
import re
import datetime
# from tabulate import tabulate
# import xml.etree.ElementTree as et

setup_test_environment()

from django.test import Client
c = Client()