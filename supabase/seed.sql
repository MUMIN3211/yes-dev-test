-- Sample data for developing the public pages before Excel import (Feature 3) exists.
-- Safe to re-run: upserts by sku. Delete these rows before importing real data if desired.

insert into public.products (sku, name, category, price, size, description, how_to_use, status)
values
    ('LS-0001', 'Gentle Foam Cleanser', 'Cleanser', 390, '150 ml',
     'Low-pH foaming cleanser that removes dirt without stripping the skin barrier.',
     'Lather a small amount with water, massage onto damp face, then rinse.', 'active'),
    ('LS-0002', 'Hydrating Toner', 'Toner', 450, '200 ml',
     'Alcohol-free toner with hyaluronic acid for instant hydration.',
     'Pat onto clean skin with palms or a cotton pad, morning and night.', 'active'),
    ('LS-0003', 'Vitamin C Bright Serum', 'Serum', 890, '30 ml',
     '10% vitamin C serum that helps even out skin tone.',
     'Apply 3-4 drops after toner every morning, follow with sunscreen.', 'active'),
    ('LS-0004', 'Barrier Repair Cream', 'Moisturizer', 690, '50 g',
     'Ceramide-rich cream that strengthens the skin barrier overnight.',
     'Apply as the last step of your evening routine.', 'active'),
    ('LS-0005', 'Daily UV Shield SPF50+', 'Sunscreen', 550, '50 ml',
     'Lightweight, non-greasy sunscreen with PA++++ protection.',
     'Apply generously 15 minutes before sun exposure; reapply every 2 hours.', 'active'),
    ('LS-0006', 'Clay Detox Mask', 'Mask', 520, '100 g',
     'Kaolin clay mask that absorbs excess oil and refines pores.',
     'Apply an even layer 1-2 times a week, leave 10 minutes, rinse off.', 'inactive')
on conflict (sku) do update set
    name = excluded.name,
    category = excluded.category,
    price = excluded.price,
    size = excluded.size,
    description = excluded.description,
    how_to_use = excluded.how_to_use,
    status = excluded.status;
