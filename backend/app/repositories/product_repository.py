from supabase import Client

TABLE = "products"
PUBLIC_COLUMNS = "sku, name, category, price, size, description, how_to_use, image_url"

# Characters with meaning in PostgREST filter syntax or LIKE patterns
_FILTER_UNSAFE = set(',()*%_"\\:')


class ProductRepository:
    """All Supabase access for the `products` table lives here."""

    def __init__(self, client: Client):
        self.client = client

    def list_active(self, category: str | None = None, search: str | None = None) -> list[dict]:
        query = self.client.table(TABLE).select(PUBLIC_COLUMNS).eq("status", "active")
        if category:
            query = query.eq("category", category)
        if search:
            term = "".join(ch for ch in search if ch not in _FILTER_UNSAFE).strip()
            if term:
                query = query.or_(f"name.ilike.%{term}%,sku.ilike.%{term}%")
        return query.order("sku").execute().data

    def get_active_by_sku(self, sku: str) -> dict | None:
        rows = (
            self.client.table(TABLE)
            .select(PUBLIC_COLUMNS)
            .eq("sku", sku)
            .eq("status", "active")
            .limit(1)
            .execute()
            .data
        )
        return rows[0] if rows else None
