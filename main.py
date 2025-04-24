from approve_fcc_orders import approve_fcc_orders
from cancel_nyc_orders import cancel_nyc_banned_ingredients

def main():
    approve_fcc_orders()
    cancel_nyc_banned_ingredients()

if __name__ == '__main__':
    main()