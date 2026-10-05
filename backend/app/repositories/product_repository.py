from supabase import Client

TABLE = "products"
PUBLIC_COLUMNS = "sku, name, category, price, size, description, how_to_use, image_url"
ADMIN_COLUMNS = f"{PUBLIC_COLUMNS}, status, updated_at"
# Columns an Excel import writes. image_url is not one of them, so re-importing
# never removes a product's photo.
IMPORT_COLUMNS = "sku, name, category, price, size, description, how_to_use, status"

# Keeps `sku=in.(...)` URLs and upsert payloads at a safe size
_CHUNK = 200

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

    # --- back office ---------------------------------------------------------

    def list_all(self) -> list[dict]:
        return self.client.table(TABLE).select(ADMIN_COLUMNS).order("sku").execute().data

    def get_by_sku(self, sku: str) -> dict | None:
        rows = self.client.table(TABLE).select(ADMIN_COLUMNS).eq("sku", sku).limit(1).execute().data
        return rows[0] if rows else None

    def get_import_fields_by_skus(self, skus: list[str]) -> dict[str, dict]:
        found: dict[str, dict] = {}
        for i in range(0, len(skus), _CHUNK):
            chunk = skus[i : i + _CHUNK]
            rows = self.client.table(TABLE).select(IMPORT_COLUMNS).in_("sku", chunk).execute().data
            found.update({row["sku"]: row for row in rows})
        return found

    def upsert_many(self, rows: list[dict]) -> None:
        """Insert new SKUs, update existing ones. Only the columns in `rows` are written."""
        for i in range(0, len(rows), _CHUNK):
            self.client.table(TABLE).upsert(rows[i : i + _CHUNK], on_conflict="sku").execute()
