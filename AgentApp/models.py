from django.db import models
from UserApp.models import *


class AgentModel(models.Model):
    """
    Model representing an agent working for the travel agency.

    Attributes:
        agent_id (AutoField): The unique identifier for the agent.
        agent_name (CharField): The name of the agent.
        agent_email (EmailField): The email address of the agent.
        agent_password (CharField): The password of the agent.
        agent_phone (CharField): The phone number of the agent.
        created_at (DateField): The date and time when the agent was created.
        license (CharField): The license number of the agent.
        status (CharField): The status of the agent (e.g., active, inactive).
    """
    agent_id = models.AutoField(primary_key=True)
    agent_name = models.CharField(max_length=255)
    agent_email = models.EmailField(max_length=255)
    agent_password = models.CharField(max_length=255)
    agent_phone = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    license = models.CharField(max_length=255)
    status = models.CharField(max_length=255)

    class Meta:
        db_table = 'agent_data'

    def __str__(self):
        return self.agent_name


class NationsModel(models.Model):
    """
    Model representing nations or countries.

    Attributes:
        nations_id (AutoField): The unique identifier for the nation.
        nation (CharField): The name of the nation.
    """
    nations_id = models.AutoField(primary_key=True)
    nation = models.CharField(max_length=255)

    class Meta:
        db_table = 'nations'

    def __str__(self):
        return self.nation


class PackageModel(models.Model):
    """
    Model representing a travel package offered by the agency.

    Attributes:
        package_id (AutoField): The unique identifier for the package.3
        destination_name (CharField): The name of the travel destination.
        created_at (Date Field): The date and time when the package was created.
        status (CharField): The status of the package (e.g., active, inactive).
        agent (ForeignKey): The agent associated with this package.
        description (TextField): The description of the package.
        price (IntegerField): The price of the package.
        nation_id (ForeignKey): The nation associated with this package.
    """
    package_id = models.AutoField(primary_key=True)
    destination_name = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=255, default='active')
    agent = models.ForeignKey(AgentModel, on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    price = models.IntegerField()
    nation_id = models.ForeignKey(NationsModel, on_delete=models.CASCADE)
    is_recommended = models.BooleanField(default=False)

    class Meta:
        db_table = 'PackageModel'

    def __str__(self):
        return self.destination_name


class PackageSplit(models.Model):
    """
    Model representing a split of a package into smaller units.

    Attributes:
        package_split_id (AutoField): The unique identifier for the package split.
        package_id (ForeignKey): The package associated with this split.
        quantity (IntegerField): The quantity of this split.
        start_date (DateField): The start date of this split.
        end_date (DateField): The end date of this split.
    """
    package_split_id = models.AutoField(primary_key=True)
    package_id = models.ForeignKey(PackageModel, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        db_table = 'package_split'


class PackageImagesModel(models.Model):
    """
    Model representing images associated with a package.

    Attributes:
        image_id (AutoField): The unique identifier for the image.
        image (ImageField): The image file.
        package_id (ForeignKey): The package associated with this image.
    """
    image_id = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='images')
    package_id = models.ForeignKey(PackageModel, related_name='images', on_delete=models.CASCADE)

    class Meta:
        db_table = 'package_images'


class OfferModel(models.Model):
    """
    Model representing special offers or promotions.
    """
    offer_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateField()
    valid_to = models.DateField()
    applicable_packages = models.ManyToManyField(PackageModel, related_name='offers')
    applicable_agents = models.ManyToManyField(AgentModel)
    status = models.CharField(max_length=255, default='active')

    class Meta:
        db_table = 'offers'

    def __str__(self):
        return self.title


class HotelModel(models.Model):
    """
    Model representing a hotel.

    Attributes:
        hotel_id (AutoField): The unique identifier for the hotel.
        hotel_name (CharField): The name of the hotel.
    """
    hotel_id = models.AutoField(primary_key=True)
    hotel_name = models.CharField(max_length=255)
    hotel_description = models.TextField(null=True)

    class Meta:
        db_table = 'hotel_data'

    def __str__(self):
        return self.hotel_name


class HotelImage(models.Model):
    """
    Model representing images associated with a hotel.

    Attributes:
        hotel_image_id (AutoField): The unique identifier for the hotel image.
        hotel_id (ForeignKey): The hotel associated with this image.
        hotel_image (ImageField): The image associated with this hotel.
    """
    hotel_image_id = models.AutoField(primary_key=True)
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE)
    hotel_image = models.ImageField(upload_to='images')

    class Meta:
        db_table = 'hotel_image'


class PackageHotel(models.Model):
    """
    Model representing the relationship between packages and hotels.

    Attributes:
        package_hotel_id (AutoField): The unique identifier for the package hotel.
        hotel_id (ForeignKey): The hotel associated with this package.
        package_split_id (ForeignKey): The package split associated with this package hotel.
        price (IntegerField): The price of this package hotel.
        quantity (IntegerField): The quantity of this package hotel.
    """
    package_hotel_id = models.AutoField(primary_key=True)
    hotel_id = models.ForeignKey(HotelModel, on_delete=models.CASCADE)
    package_split_id = models.ForeignKey(PackageSplit, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.IntegerField()

    class Meta:
        db_table = 'package_hotel'


class ActivitiesModel(models.Model):
    """
    Model representing activities included in a package.

    Attributes:
        activities_id (AutoField): The unique identifier for the activity.
        activities (CharField): The name of the activity.
        activity_description (CharField): The description of the activity.
        package_id (ForeignKey): The package associated with this activity.
    """
    activities_id = models.AutoField(primary_key=True)
    activities = models.CharField(max_length=255, null=True)
    activity_images = models.ImageField(upload_to='images/', null=True)
    activity_description = models.CharField(max_length=255, null=True)
    package_id = models.ForeignKey(PackageModel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'activities'

    def __str__(self):
        return self.activities
