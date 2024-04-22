from django.db import models
from AgentApp.models import *
from AgentApp.models import PackageModel, PackageHotel


class UserModel(models.Model):
    """
    Model representing a user of the travel agency's system.

    Attributes:
        user_id (AutoField): The unique identifier for the user.
        user_name (CharField): The name of the user.
        user_email (EmailField): The email address of the user.
        user_password (CharField): The password of the user.
        created_at (DateTimeField): The date and time when the user was created.
        status (CharField): The status of the user (e.g., active, inactive).
    """
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    user_email = models.EmailField(max_length=255)
    user_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=255, default='Active')

    class Meta:
        db_table = 'user_data'

    def __str__(self):
        return self.user_name


class FeedbackModel(models.Model):
    """
    Model representing feedback provided by users for packages.

    Attributes:
        user_id (ForeignKey): The user who provided the feedback.
        package_id (ForeignKey): The package for which the feedback is provided.
        rating (IntegerField): The rating given by the user.
        review (TextField): The review provided by the user.
    """
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    package_id = models.ForeignKey(PackageModel, on_delete=models.CASCADE, null=False)
    rating = models.IntegerField(default=1)
    review = models.TextField(max_length=500)

    class Meta:
        db_table = 'feedback'

    def __str__(self):
        return self.review


class WishlistModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    package = models.ForeignKey(PackageModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wishlist'
        unique_together = ['user', 'package']


class WebsiteReviewModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    review_text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'website_review'

    def __str__(self):
        return self.user


class PaymentType(models.Model):
    """
    Model representing types of payment.

    Attributes:
        payment_id (AutoField): The unique identifier for the payment type.
        payment_type (CharField): The type of payment (e.g., credit card, PayPal).
    """
    payment_id = models.AutoField(primary_key=True)
    payment_type = models.CharField(max_length=255)

    class Meta:
        db_table = 'payment_type'

    def __str__(self):
        return self.payment_type


class BookingModel(models.Model):
    """
    Model representing a booking made by a user.

    Attributes:
        booking_id (AutoField): The unique identifier for the booking.
        from_date (DateField): The start date of the booking.
        to_date (DateField): The end date of the booking.
        total_price (IntegerField): The total price of the booking.
        created_at (DateTimeField): The date and time when the booking was created.
        num_adult (IntegerField): The number of adult guests.
        num_children (IntegerField): The number of child guests.
        special_request (CharField): Any special requests from the user.
        payment_status (CharField): The status of the payment for the booking.
        user_id (ForeignKey): The user who made the booking.
        package_hotel_id (ForeignKey): The package hotel associated with this booking.
        status (CharField): The status of the booking (e.g., pending, confirmed).
    """
    booking_id = models.AutoField(primary_key=True)
    from_date = models.DateField()
    to_date = models.DateField()
    total_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    num_adult = models.IntegerField()
    num_children = models.IntegerField()
    booking_status = models.CharField(max_length=255, default="pending")
    payment_status = models.CharField(max_length=255, default="pending")
    car_rental = models.CharField(max_length=255, null=True)
    package_id = models.ForeignKey(PackageModel, on_delete=models.CASCADE, null=True)
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    package_hotel_id = models.ForeignKey(PackageHotel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'booking'


class PaymentModel(models.Model):
    """
    Model representing a payment made by a user for a booking.

    Attributes:
        payment_id (AutoField): The unique identifier for the payment.
        user_id (ForeignKey): The user who made the payment.
        booking_id (ForeignKey): The booking associated with this payment.
        payment_type (ForeignKey): The type of payment used.
        amount (IntegerField): The amount of the payment.
        payment_status (CharField): The status of the payment (e.g., pending, complete).
    """
    payment_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    booking_id = models.ForeignKey(BookingModel, on_delete=models.CASCADE)
    payment_type = models.ForeignKey(PaymentType, on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_status = models.CharField(max_length=255)

    class Meta:
        db_table = 'payment'

    def __str__(self):
        return self.payment_type
