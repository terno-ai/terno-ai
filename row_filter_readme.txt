sales

row_filter:
    - tablle: sales
    - filter: company_id = 10 and category_id not in (1, 2, 3)
person is part of both: Groceries, Electronics

group_row_filter:
    - group: Groceries
    - filter: category_id = 12

group_row_filter:
    - group: Electronics
    - filter: category_id = 13

table filter generated for this sales table and this person:
    where (
    (company_id = 10 and category_id not in (1, 2, 3))
    AND (
            (category_id = 12)
            OR 
            (category_id = 13)
        )
    )