
--Data Analysis using SQL:

--1] Top 10 company with higest total cost of products
select top 10 Company,sum(cast(price as float)) Total_cost from medicine group by Company order by 2 desc

--2] Top 5 Most expensive product based on category
with cte as
(select Product_Name,max(price) over (partition by category order by price desc) price, Category,dense_rank() over (partition by category order by price desc) as rn from medicine)
select Product_Name,price,Category from cte where rn<6

--3] Top 5 company with most number of product 
select top 5 Company,count(Product_Name) as total_products  from medicine group by Company order by 2 desc

--4] Most used composition2 in the process type filling
select top 10 Composition2,count(id) as total from medicine where process_type='filling' group by Composition2 order by 2 desc

--5] Top 5 category with most number of products
select top 5 Category,count(Product_Name) as total_products  from medicine group by Category order by 2 desc

--6} Product with differnt strengths present in the indian market
with  cte as (
SELECT 
    Product_Name,
  Category,
      Strength,
    Company,COUNT(*) over(partition by product,category ORDER BY 
    Product_Name, Strength) as total_count

FROM 
    medicine where Category<>'other')
select Product_Name,Category,Strength,Company from cte where Product_Name in(select Product_Name from cte where total_count>1) 
order by total_count desc


--7. **Market Share Analysis:** Determine the market share of each company based on the total sales value of their products.

SELECT 
    Company,
    ROUND(SUM(Price),2) AS Total_Sales,
   ROUND((SUM(Price) / (SELECT SUM(Price) FROM medicine)) * 100,2) AS Market_Share 
FROM 
    medicine 
GROUP BY 
    Company  
ORDER BY  
    Total_Sales DESC;


--8. **Price Variation Analysis:** Identify the average, minimum, and maximum prices for different types of products (e.g., tablets, capsules, syrups) across different companies.
SELECT 
    Category,
    Company,
    AVG(Price) AS Avg_Price,
    MIN(Price) AS Min_Price,
    MAX(Price) AS Max_Price
FROM 
    medicine
GROUP BY 
    Category, Company;

--9. **Composition Comparison:** Analyze the distribution of compositions (Composition1 and Composition2) across different categories of products and identify the most commonly used compositions.
SELECT 
    Composition,
    COUNT(*) AS Product_Count
FROM 
    (
    SELECT Composition1 AS Composition FROM medicine
    UNION ALL
    SELECT Composition2 FROM medicine
    ) AS compositions
GROUP BY 
    Composition
ORDER BY 
    Product_Count DESC;




--10) Market share analysis by category

WITH category_sales AS (
    SELECT 
        Category,
        SUM(Price) AS Total_Sales
    FROM 
        medicine
    GROUP BY 
        Category
),
total_sales AS (
    SELECT SUM(Price) AS Total FROM medicine
)
SELECT 
    category,
    Total_Sales,
    round((Total_Sales / (SELECT Total FROM total_sales)) * 100 ,2)AS Market_Share
FROM 
    category_sales;

--11]The market share of the top 5 companies within each category, along with their total sales and market share percentage.

WITH category_company_sales AS (
    SELECT 
        Category,
        Company,
        SUM(Price) AS Total_Sales,
        ROW_NUMBER() OVER (PARTITION BY Category ORDER BY SUM(Price) DESC) AS company_rank
    FROM 
        medicine
    GROUP BY 
        Category, Company
),
total_category_sales AS (
    SELECT 
        Category,
        SUM(Price) AS Total_Sales
    FROM 
        medicine
    GROUP BY 
        Category
)
SELECT 
    Category,
    Company,
    Total_Sales,
    ROUND((Total_Sales / (SELECT Total_Sales FROM total_category_sales WHERE Category = cc.Category)) * 100, 2) AS Market_Share
FROM 
    category_company_sales cc
WHERE 
    company_rank <= 5;



