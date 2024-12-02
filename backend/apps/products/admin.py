from django.contrib import admin
from .models import (
    Bank, 
    DepositProduct, 
    SavingProduct, 
    DepositOption,
    SavingOption,
    UserFinancialProduct
)

admin.site.register(Bank)
admin.site.register(DepositProduct)
admin.site.register(SavingProduct)
admin.site.register(DepositOption)
admin.site.register(SavingOption)
admin.site.register(UserFinancialProduct)