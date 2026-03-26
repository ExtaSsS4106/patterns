from django.db import models
from django.contrib.auth.models import User

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45, blank=True, null=True, unique=True)

    class Meta:
        db_table = 'categories'

class Stacks(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'stacks'


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'tags'
           
class Patterns(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=45)
    categories = models.ForeignKey(Categories, on_delete=models.DO_NOTHING, db_column='categories_id')
    term = models.TextField()
    problem = models.TextField()
    solution = models.TextField()
    examples = models.TextField()
    consclusions = models.TextField()

    tags = models.ManyToManyField(Tags, blank=True)
    stacks = models.ManyToManyField(Stacks, blank=True)
    class Meta:
        db_table = 'patterns'
        unique_together = (('id', 'categories'),)


class Profiles(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'users'



class Favorites(models.Model):
    id = models.AutoField(primary_key=True)
    users = models.ForeignKey(Profiles, on_delete=models.DO_NOTHING, db_column='users_id')
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')

    class Meta:
        db_table = 'favorites'
        unique_together = (('id', 'users', 'patterns'),)





class StackPattern(models.Model):
    id = models.AutoField(primary_key=True)
    stacks = models.ForeignKey(Stacks, on_delete=models.DO_NOTHING, db_column='stacks_id')
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')

    class Meta:
        db_table = 'stack_pattern'
        unique_together = (('id', 'stacks', 'patterns'),)




class TagPattern(models.Model):
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')
    tags = models.ForeignKey(Tags, on_delete=models.DO_NOTHING, db_column='tags_id')

    class Meta:
        db_table = 'tag_pattern'
        unique_together = (('patterns', 'tags'),)


class Ratings(models.Model):
    id = models.AutoField(primary_key=True)
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')
    likes = models.IntegerField(blank=True, null=True)
    dislikes = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ratings'
        unique_together = (('id', 'patterns'),)

class Rating_profiles(models.Model):
    id = models.AutoField(primary_key=True)
    profiles = models.ForeignKey(Profiles, on_delete=models.CASCADE)
    ratings = models.ForeignKey(Ratings, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=[('none', 'none'), ('like', 'like'), ('dislike', 'dislike')],
        db_column='status',
        default='none'
    )
    like = models.BooleanField(default=False)
    dislike = models.BooleanField(default=False)
    class Meta:
        db_table = 'rating_profiles'
        unique_together = (('id'),)

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')
    users = models.ForeignKey(Profiles, on_delete=models.DO_NOTHING, db_column='users_id')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) 
    class Meta:
        db_table = 'comments'
        unique_together = (('id', 'patterns', 'users'),)


class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateField(auto_now=True, blank=True, null=True)
    patterns = models.ForeignKey(Patterns, on_delete=models.DO_NOTHING, db_column='patterns_id')

    class Meta:
        db_table = 'logs'
        unique_together = (('id', 'patterns'),)