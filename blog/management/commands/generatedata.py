from django.core.management.base import BaseCommand
from datetime import datetime
from faker import Faker
import random
from blog.models import *
from types import FunctionType
from functools import wraps

USER_COUNT = 5
TAG_COUNT = 30
POST_COUNT = 100


class Command(BaseCommand):

    def handle(self, *args, **options):
        #self.create_users()
        #self.create_profiles()
        self.create_tags()

    def create_users(self):
        users = []
        faker = Faker()
        for i in range(USER_COUNT):
            user = MyUser(username=faker.user_name() + str(i), password='userPassword{}'.format(i), email=faker.email())
            users.append(user)
        MyUser.objects.bulk_create(users, batch_size=10000)

    def create_profiles(self):
        profiles = []
        users = MyUser.objects.all()
        for user in users:
            profile = UserProfile.objects.create(user=user)
            profiles.append(profile)
        UserProfile.objects.bulk_create(profiles, batch_size=10000)

    def create_tags(self):
        tags = []
        faker = Faker()
        for i in range(TAG_COUNT):
            tag = Tag(title=faker.word() + str(i))
            tags.append(tag)
        Tag.objects.bulk_create(tags, batch_size=10000)

    def create_posts(self):
        users = MyUser.objects.all()
        faker = Faker()
        for i in range(POST_COUNT):
            tags = Tag.objects.filter()
            post = Post(title=faker.sentence()[:random.randint(20, 100)],
                        text=faker.text(),
                        author=random.choice(users))


