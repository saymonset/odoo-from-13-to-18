pls = env['product.pricelist'].search([])
for pl in pls:
    print(f'Pricelist: {pl.name}, Currency: {pl.currency_id.name}')
