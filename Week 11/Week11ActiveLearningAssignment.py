import argparse
import sys
import psycopg2
import matplotlib.pyplot as plt


def main(category_name: str):
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="week11_assignment",
        user="postgres",
        password="chubbs1"
    )
    cursor = conn.cursor()

    query = f"""
        SELECT {category_name}, AVG(mean_ghg_1990_to_2020) as avg_ghg
        FROM epa_ghg
        GROUP BY {category_name}
        ORDER BY avg_ghg DESC;
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    categories = [row[0] for row in rows]
    values = [float(row[1]) for row in rows]

    plt.figure(figsize=(10, 6))
    plt.bar(categories, values, color='steelblue')
    plt.title(f'Average GHG 1990–2020 by {category_name}')
    plt.xlabel(category_name)
    plt.ylabel('Average GHG')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    cursor.close()
    conn.close()


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('category_name', type=str,
                        choices=['ECON_SECTOR', 'SECTOR', 'SUBSECTOR', 'CATEGORY', 'STATE', 'GHG'],
                        help='Column name to group by')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    sys.exit(main(args.category_name))