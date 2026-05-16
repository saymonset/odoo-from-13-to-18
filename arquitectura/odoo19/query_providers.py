providers = env['currency.rate.provider'].search([])
for p in providers:
    print(f'ID: {p.id}, Name: {p.name}, Main: {p.is_main_rate}, RateCurr: {p.rate_currency_id.name}')
