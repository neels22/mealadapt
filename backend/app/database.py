import aiosqlite
import json
import os
from typing import List, Optional
from app.models.family import FamilyMember, FamilyProfile, HealthCondition, Role, ConditionType

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "..", "mainmeal.db")


async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Create users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create family_members table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS family_members (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                avatar TEXT DEFAULT '😊',
                role TEXT DEFAULT 'Adult',
                custom_restrictions TEXT,
                preferences TEXT
            )
        """)
        
        # Create health_conditions table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS health_conditions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id TEXT REFERENCES family_members(id) ON DELETE CASCADE,
                condition_type TEXT NOT NULL,
                enabled INTEGER DEFAULT 0,
                notes TEXT
            )
        """)
        
        # Create pantry_items table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pantry_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                category TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create saved_recipes table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_recipes (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                dish_name TEXT NOT NULL,
                recipe_text TEXT,
                analysis_json TEXT,
                is_favorite INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create recipe_tags table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS recipe_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id TEXT REFERENCES saved_recipes(id) ON DELETE CASCADE,
                tag TEXT NOT NULL
            )
        """)
        
        # Create shopping_lists table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Create shopping_items table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS shopping_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id TEXT REFERENCES shopping_lists(id) ON DELETE CASCADE,
                ingredient TEXT NOT NULL,
                quantity TEXT,
                category TEXT,
                is_checked INTEGER DEFAULT 0,
                source_recipe_id TEXT
            )
        """)
        
        # Create meal_plans table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS meal_plans (
                id TEXT PRIMARY KEY,
                user_id TEXT REFERENCES users(id) ON DELETE CASCADE,
                week_start DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create planned_meals table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS planned_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id TEXT REFERENCES meal_plans(id) ON DELETE CASCADE,
                recipe_id TEXT REFERENCES saved_recipes(id),
                date DATE NOT NULL,
                meal_type TEXT NOT NULL,
                servings INTEGER DEFAULT 1,
                notes TEXT
            )
        """)
        
        # Create barcode_cache table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS barcode_cache (
                barcode TEXT PRIMARY KEY,
                product_data TEXT NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create refresh_tokens table for JWT refresh token management
        await db.execute("""
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                jti TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create blacklisted_tokens table for revoked tokens
        await db.execute("""
            CREATE TABLE IF NOT EXISTS blacklisted_tokens (
                jti TEXT PRIMARY KEY,
                token_type TEXT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: Add user_id column to existing tables if they don't have it
        # Check and add user_id to family_members
        cursor = await db.execute("PRAGMA table_info(family_members)")
        columns = [row[1] for row in await cursor.fetchall()]
        if 'user_id' not in columns:
            await db.execute("ALTER TABLE family_members ADD COLUMN user_id TEXT REFERENCES users(id)")
            print("✅ Added user_id column to family_members")
        
        # Check and add user_id to pantry_items
        cursor = await db.execute("PRAGMA table_info(pantry_items)")
        columns = [row[1] for row in await cursor.fetchall()]
        if 'user_id' not in columns:
            await db.execute("ALTER TABLE pantry_items ADD COLUMN user_id TEXT REFERENCES users(id)")
            print("✅ Added user_id column to pantry_items")
        
        await db.commit()
        print("✅ Database initialized successfully")


async def get_all_members(user_id: Optional[str] = None) -> List[FamilyMember]:
    """Get all family members with their conditions, optionally filtered by user_id"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Get all members (filtered by user_id if provided)
        if user_id:
            cursor = await db.execute(
                "SELECT * FROM family_members WHERE user_id = ?",
                (user_id,)
            )
        else:
            cursor = await db.execute("SELECT * FROM family_members WHERE user_id IS NULL")
        rows = await cursor.fetchall()
        
        members = []
        for row in rows:
            # Get conditions for this member
            cond_cursor = await db.execute(
                "SELECT * FROM health_conditions WHERE member_id = ?",
                (row["id"],)
            )
            cond_rows = await cond_cursor.fetchall()
            
            conditions = [
                HealthCondition(
                    type=ConditionType(cond["condition_type"]),
                    enabled=bool(cond["enabled"]),
                    notes=cond["notes"]
                )
                for cond in cond_rows
            ]
            
            member = FamilyMember(
                id=row["id"],
                name=row["name"],
                avatar=row["avatar"],
                role=Role(row["role"]),
                conditions=conditions,
                custom_restrictions=json.loads(row["custom_restrictions"] or "[]"),
                preferences=json.loads(row["preferences"] or "null")
            )
            members.append(member)
        
        return members


async def get_member_by_id(member_id: str) -> Optional[FamilyMember]:
    """Get a single family member by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM family_members WHERE id = ?",
            (member_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        # Get conditions
        cond_cursor = await db.execute(
            "SELECT * FROM health_conditions WHERE member_id = ?",
            (member_id,)
        )
        cond_rows = await cond_cursor.fetchall()
        
        conditions = [
            HealthCondition(
                type=ConditionType(cond["condition_type"]),
                enabled=bool(cond["enabled"]),
                notes=cond["notes"]
            )
            for cond in cond_rows
        ]
        
        return FamilyMember(
            id=row["id"],
            name=row["name"],
            avatar=row["avatar"],
            role=Role(row["role"]),
            conditions=conditions,
            custom_restrictions=json.loads(row["custom_restrictions"] or "[]"),
            preferences=json.loads(row["preferences"] or "null")
        )


async def add_member(member: FamilyMember, user_id: Optional[str] = None) -> FamilyMember:
    """Add a new family member"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO family_members (id, user_id, name, avatar, role, custom_restrictions, preferences)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                member.id,
                user_id,
                member.name,
                member.avatar,
                member.role.value,
                json.dumps(member.custom_restrictions),
                json.dumps(member.preferences)
            )
        )
        
        # Add conditions
        for condition in member.conditions:
            await db.execute(
                """INSERT INTO health_conditions (member_id, condition_type, enabled, notes)
                   VALUES (?, ?, ?, ?)""",
                (member.id, condition.type.value, int(condition.enabled), condition.notes)
            )
        
        await db.commit()
        return member


async def update_member(member_id: str, member: FamilyMember) -> Optional[FamilyMember]:
    """Update an existing family member"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if member exists
        cursor = await db.execute(
            "SELECT id FROM family_members WHERE id = ?",
            (member_id,)
        )
        if not await cursor.fetchone():
            return None
        
        # Update member
        await db.execute(
            """UPDATE family_members 
               SET name = ?, avatar = ?, role = ?, custom_restrictions = ?, preferences = ?
               WHERE id = ?""",
            (
                member.name,
                member.avatar,
                member.role.value,
                json.dumps(member.custom_restrictions),
                json.dumps(member.preferences),
                member_id
            )
        )
        
        # Delete old conditions and insert new ones
        await db.execute(
            "DELETE FROM health_conditions WHERE member_id = ?",
            (member_id,)
        )
        
        for condition in member.conditions:
            await db.execute(
                """INSERT INTO health_conditions (member_id, condition_type, enabled, notes)
                   VALUES (?, ?, ?, ?)""",
                (member_id, condition.type.value, int(condition.enabled), condition.notes)
            )
        
        await db.commit()
        member.id = member_id
        return member


async def delete_member(member_id: str) -> bool:
    """Delete a family member"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if member exists
        cursor = await db.execute(
            "SELECT id FROM family_members WHERE id = ?",
            (member_id,)
        )
        if not await cursor.fetchone():
            return False
        
        # Delete conditions first (foreign key)
        await db.execute(
            "DELETE FROM health_conditions WHERE member_id = ?",
            (member_id,)
        )
        
        # Delete member
        await db.execute(
            "DELETE FROM family_members WHERE id = ?",
            (member_id,)
        )
        
        await db.commit()
        return True


# Pantry functions
async def get_pantry_items(user_id: Optional[str] = None) -> List[dict]:
    """Get all pantry items, optionally filtered by user_id"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        if user_id:
            cursor = await db.execute(
                "SELECT * FROM pantry_items WHERE user_id = ? ORDER BY added_at DESC",
                (user_id,)
            )
        else:
            cursor = await db.execute("SELECT * FROM pantry_items WHERE user_id IS NULL ORDER BY added_at DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def add_pantry_item(name: str, category: str = None, user_id: Optional[str] = None) -> dict:
    """Add an item to the pantry"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO pantry_items (name, category, user_id) VALUES (?, ?, ?)",
            (name, category, user_id)
        )
        await db.commit()
        return {"id": cursor.lastrowid, "name": name, "category": category}


async def delete_pantry_item(item_id: int, user_id: Optional[str] = None) -> bool:
    """Delete a pantry item"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if user_id:
            cursor = await db.execute(
                "SELECT id FROM pantry_items WHERE id = ? AND user_id = ?",
                (item_id, user_id)
            )
        else:
            cursor = await db.execute(
                "SELECT id FROM pantry_items WHERE id = ? AND user_id IS NULL",
                (item_id,)
            )
        if not await cursor.fetchone():
            return False
        
        await db.execute("DELETE FROM pantry_items WHERE id = ?", (item_id,))
        await db.commit()
        return True


async def clear_pantry(user_id: Optional[str] = None) -> None:
    """Clear all pantry items for a user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        if user_id:
            await db.execute("DELETE FROM pantry_items WHERE user_id = ?", (user_id,))
        else:
            await db.execute("DELETE FROM pantry_items WHERE user_id IS NULL")
        await db.commit()


# User functions
async def create_user(user_id: str, email: str, password_hash: str, name: str) -> dict:
    """Create a new user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO users (id, email, password_hash, name)
               VALUES (?, ?, ?, ?)""",
            (user_id, email, password_hash, name)
        )
        await db.commit()
        return {"id": user_id, "email": email, "name": name}


async def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Get user by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def update_user(user_id: str, name: Optional[str] = None, email: Optional[str] = None, password_hash: Optional[str] = None) -> Optional[dict]:
    """Update user details"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Build update query dynamically
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if password_hash is not None:
            updates.append("password_hash = ?")
            params.append(password_hash)
        
        if not updates:
            return await get_user_by_id(user_id)
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        await db.execute(query, params)
        await db.commit()
        
        return await get_user_by_id(user_id)


async def delete_user(user_id: str) -> bool:
    """Delete a user and all their data"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not await cursor.fetchone():
            return False
        
        # Delete user's pantry items
        await db.execute("DELETE FROM pantry_items WHERE user_id = ?", (user_id,))
        
        # Delete user's meal plans (planned meals will cascade)
        await db.execute("DELETE FROM planned_meals WHERE plan_id IN (SELECT id FROM meal_plans WHERE user_id = ?)", (user_id,))
        await db.execute("DELETE FROM meal_plans WHERE user_id = ?", (user_id,))
        
        # Delete user's shopping lists (items will cascade)
        await db.execute("DELETE FROM shopping_items WHERE list_id IN (SELECT id FROM shopping_lists WHERE user_id = ?)", (user_id,))
        await db.execute("DELETE FROM shopping_lists WHERE user_id = ?", (user_id,))
        
        # Delete user's saved recipes (tags will cascade)
        await db.execute("DELETE FROM recipe_tags WHERE recipe_id IN (SELECT id FROM saved_recipes WHERE user_id = ?)", (user_id,))
        await db.execute("DELETE FROM saved_recipes WHERE user_id = ?", (user_id,))
        
        # Delete user's family members (conditions will cascade)
        await db.execute("DELETE FROM health_conditions WHERE member_id IN (SELECT id FROM family_members WHERE user_id = ?)", (user_id,))
        await db.execute("DELETE FROM family_members WHERE user_id = ?", (user_id,))
        
        # Delete user
        await db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        await db.commit()
        return True


# Saved Recipes functions
async def get_saved_recipes(user_id: str, favorites_only: bool = False) -> List[dict]:
    """Get all saved recipes for a user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        query = "SELECT * FROM saved_recipes WHERE user_id = ?"
        params = [user_id]
        
        if favorites_only:
            query += " AND is_favorite = 1"
        
        query += " ORDER BY created_at DESC"
        
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        
        recipes = []
        for row in rows:
            recipe = dict(row)
            # Parse analysis_json
            if recipe.get("analysis_json"):
                recipe["analysis"] = json.loads(recipe["analysis_json"])
            else:
                recipe["analysis"] = None
            del recipe["analysis_json"]
            
            # Get tags for this recipe
            tag_cursor = await db.execute(
                "SELECT tag FROM recipe_tags WHERE recipe_id = ?",
                (recipe["id"],)
            )
            tag_rows = await tag_cursor.fetchall()
            recipe["tags"] = [row["tag"] for row in tag_rows]
            
            recipes.append(recipe)
        
        return recipes


async def get_saved_recipe_by_id(recipe_id: str, user_id: str) -> Optional[dict]:
    """Get a single saved recipe by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM saved_recipes WHERE id = ? AND user_id = ?",
            (recipe_id, user_id)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        recipe = dict(row)
        # Parse analysis_json
        if recipe.get("analysis_json"):
            recipe["analysis"] = json.loads(recipe["analysis_json"])
        else:
            recipe["analysis"] = None
        del recipe["analysis_json"]
        
        # Get tags
        tag_cursor = await db.execute(
            "SELECT tag FROM recipe_tags WHERE recipe_id = ?",
            (recipe_id,)
        )
        tag_rows = await tag_cursor.fetchall()
        recipe["tags"] = [row["tag"] for row in tag_rows]
        
        return recipe


async def save_recipe(
    recipe_id: str,
    user_id: str,
    dish_name: str,
    recipe_text: str,
    analysis: dict,
    tags: List[str] = None,
    notes: str = None
) -> dict:
    """Save a new recipe"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO saved_recipes (id, user_id, dish_name, recipe_text, analysis_json, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (recipe_id, user_id, dish_name, recipe_text, json.dumps(analysis), notes)
        )
        
        # Add tags if provided
        if tags:
            for tag in tags:
                await db.execute(
                    "INSERT INTO recipe_tags (recipe_id, tag) VALUES (?, ?)",
                    (recipe_id, tag)
                )
        
        await db.commit()
        
        return await get_saved_recipe_by_id(recipe_id, user_id)


async def update_saved_recipe(
    recipe_id: str,
    user_id: str,
    is_favorite: bool = None,
    notes: str = None,
    tags: List[str] = None
) -> Optional[dict]:
    """Update a saved recipe"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Check if recipe exists and belongs to user
        cursor = await db.execute(
            "SELECT id FROM saved_recipes WHERE id = ? AND user_id = ?",
            (recipe_id, user_id)
        )
        if not await cursor.fetchone():
            return None
        
        # Build update query
        updates = []
        params = []
        
        if is_favorite is not None:
            updates.append("is_favorite = ?")
            params.append(int(is_favorite))
        
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if updates:
            params.append(recipe_id)
            query = f"UPDATE saved_recipes SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
        
        # Update tags if provided
        if tags is not None:
            await db.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (recipe_id,))
            for tag in tags:
                await db.execute(
                    "INSERT INTO recipe_tags (recipe_id, tag) VALUES (?, ?)",
                    (recipe_id, tag)
                )
        
        await db.commit()
        
        return await get_saved_recipe_by_id(recipe_id, user_id)


async def delete_saved_recipe(recipe_id: str, user_id: str) -> bool:
    """Delete a saved recipe"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM saved_recipes WHERE id = ? AND user_id = ?",
            (recipe_id, user_id)
        )
        if not await cursor.fetchone():
            return False
        
        # Delete tags first
        await db.execute("DELETE FROM recipe_tags WHERE recipe_id = ?", (recipe_id,))
        
        # Delete recipe
        await db.execute("DELETE FROM saved_recipes WHERE id = ?", (recipe_id,))
        
        await db.commit()
        return True


# Shopping List functions
async def get_shopping_lists(user_id: str) -> List[dict]:
    """Get all shopping lists for a user"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM shopping_lists WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        rows = await cursor.fetchall()
        
        lists = []
        for row in rows:
            shopping_list = dict(row)
            
            # Get items for this list
            items_cursor = await db.execute(
                "SELECT * FROM shopping_items WHERE list_id = ? ORDER BY category, ingredient",
                (shopping_list["id"],)
            )
            items_rows = await items_cursor.fetchall()
            shopping_list["items"] = [dict(item) for item in items_rows]
            
            lists.append(shopping_list)
        
        return lists


async def get_shopping_list_by_id(list_id: str, user_id: str) -> Optional[dict]:
    """Get a single shopping list by ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM shopping_lists WHERE id = ? AND user_id = ?",
            (list_id, user_id)
        )
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        shopping_list = dict(row)
        
        # Get items
        items_cursor = await db.execute(
            "SELECT * FROM shopping_items WHERE list_id = ? ORDER BY category, ingredient",
            (list_id,)
        )
        items_rows = await items_cursor.fetchall()
        shopping_list["items"] = [dict(item) for item in items_rows]
        
        return shopping_list


async def create_shopping_list(
    list_id: str,
    user_id: str,
    name: str,
    items: List[dict] = None
) -> dict:
    """Create a new shopping list"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "INSERT INTO shopping_lists (id, user_id, name) VALUES (?, ?, ?)",
            (list_id, user_id, name)
        )
        
        # Add items if provided
        if items:
            for item in items:
                await db.execute(
                    """INSERT INTO shopping_items (list_id, ingredient, quantity, category, source_recipe_id)
                       VALUES (?, ?, ?, ?, ?)""",
                    (list_id, item["ingredient"], item.get("quantity"), item.get("category"), item.get("source_recipe_id"))
                )
        
        await db.commit()
        
        return await get_shopping_list_by_id(list_id, user_id)


async def add_shopping_item(
    list_id: str,
    user_id: str,
    ingredient: str,
    quantity: str = None,
    category: str = None
) -> Optional[dict]:
    """Add an item to a shopping list"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Verify list belongs to user
        cursor = await db.execute(
            "SELECT id FROM shopping_lists WHERE id = ? AND user_id = ?",
            (list_id, user_id)
        )
        if not await cursor.fetchone():
            return None
        
        cursor = await db.execute(
            """INSERT INTO shopping_items (list_id, ingredient, quantity, category)
               VALUES (?, ?, ?, ?)""",
            (list_id, ingredient, quantity, category)
        )
        await db.commit()
        
        return {"id": cursor.lastrowid, "ingredient": ingredient, "quantity": quantity, "category": category, "is_checked": 0}


async def update_shopping_item(
    item_id: int,
    user_id: str,
    is_checked: bool = None,
    quantity: str = None
) -> Optional[dict]:
    """Update a shopping item"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Verify item belongs to user's list
        cursor = await db.execute(
            """SELECT si.* FROM shopping_items si
               JOIN shopping_lists sl ON si.list_id = sl.id
               WHERE si.id = ? AND sl.user_id = ?""",
            (item_id, user_id)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        
        updates = []
        params = []
        
        if is_checked is not None:
            updates.append("is_checked = ?")
            params.append(int(is_checked))
        
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)
        
        if updates:
            params.append(item_id)
            query = f"UPDATE shopping_items SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()
        
        # Return updated item
        cursor = await db.execute("SELECT * FROM shopping_items WHERE id = ?", (item_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def delete_shopping_item(item_id: int, user_id: str) -> bool:
    """Delete a shopping item"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Verify item belongs to user's list
        cursor = await db.execute(
            """SELECT si.id FROM shopping_items si
               JOIN shopping_lists sl ON si.list_id = sl.id
               WHERE si.id = ? AND sl.user_id = ?""",
            (item_id, user_id)
        )
        if not await cursor.fetchone():
            return False
        
        await db.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
        await db.commit()
        return True


async def delete_shopping_list(list_id: str, user_id: str) -> bool:
    """Delete a shopping list and all its items"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM shopping_lists WHERE id = ? AND user_id = ?",
            (list_id, user_id)
        )
        if not await cursor.fetchone():
            return False
        
        # Delete items first
        await db.execute("DELETE FROM shopping_items WHERE list_id = ?", (list_id,))
        
        # Delete list
        await db.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))
        
        await db.commit()
        return True


async def complete_shopping_list(list_id: str, user_id: str) -> Optional[dict]:
    """Mark a shopping list as completed"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT id FROM shopping_lists WHERE id = ? AND user_id = ?",
            (list_id, user_id)
        )
        if not await cursor.fetchone():
            return None
        
        await db.execute(
            "UPDATE shopping_lists SET completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (list_id,)
        )
        await db.commit()
        
        return await get_shopping_list_by_id(list_id, user_id)


# Meal Plan functions
async def get_or_create_meal_plan(user_id: str, week_start: str, plan_id: str = None) -> dict:
    """Get meal plan for a week, creating if it doesn't exist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Check if plan exists for this week
        cursor = await db.execute(
            "SELECT * FROM meal_plans WHERE user_id = ? AND week_start = ?",
            (user_id, week_start)
        )
        row = await cursor.fetchone()
        
        if row:
            plan = dict(row)
        else:
            # Create new plan
            import uuid
            new_id = plan_id or str(uuid.uuid4())
            await db.execute(
                "INSERT INTO meal_plans (id, user_id, week_start) VALUES (?, ?, ?)",
                (new_id, user_id, week_start)
            )
            await db.commit()
            plan = {"id": new_id, "user_id": user_id, "week_start": week_start}
        
        # Get planned meals
        meals_cursor = await db.execute(
            """SELECT pm.*, sr.dish_name, sr.analysis_json 
               FROM planned_meals pm 
               LEFT JOIN saved_recipes sr ON pm.recipe_id = sr.id
               WHERE pm.plan_id = ?
               ORDER BY pm.date, pm.meal_type""",
            (plan["id"],)
        )
        meals_rows = await meals_cursor.fetchall()
        
        plan["meals"] = []
        for meal in meals_rows:
            meal_dict = dict(meal)
            # Parse analysis if present
            if meal_dict.get("analysis_json"):
                meal_dict["analysis"] = json.loads(meal_dict["analysis_json"])
                del meal_dict["analysis_json"]
            plan["meals"].append(meal_dict)
        
        return plan


async def add_planned_meal(
    plan_id: str,
    user_id: str,
    recipe_id: str,
    date: str,
    meal_type: str,
    servings: int = 1,
    notes: str = None
) -> Optional[dict]:
    """Add a meal to the plan"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Verify plan belongs to user
        cursor = await db.execute(
            "SELECT id FROM meal_plans WHERE id = ? AND user_id = ?",
            (plan_id, user_id)
        )
        if not await cursor.fetchone():
            return None
        
        # Insert the planned meal
        cursor = await db.execute(
            """INSERT INTO planned_meals (plan_id, recipe_id, date, meal_type, servings, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (plan_id, recipe_id, date, meal_type, servings, notes)
        )
        meal_id = cursor.lastrowid
        await db.commit()
        
        # Get the inserted meal with recipe info
        cursor = await db.execute(
            """SELECT pm.*, sr.dish_name, sr.analysis_json 
               FROM planned_meals pm 
               LEFT JOIN saved_recipes sr ON pm.recipe_id = sr.id
               WHERE pm.id = ?""",
            (meal_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            meal = dict(row)
            if meal.get("analysis_json"):
                meal["analysis"] = json.loads(meal["analysis_json"])
                del meal["analysis_json"]
            return meal
        return None


async def update_planned_meal(
    meal_id: int,
    user_id: str,
    recipe_id: str = None,
    date: str = None,
    meal_type: str = None,
    servings: int = None,
    notes: str = None
) -> Optional[dict]:
    """Update a planned meal"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        # Verify meal belongs to user's plan
        cursor = await db.execute(
            """SELECT pm.id FROM planned_meals pm
               JOIN meal_plans mp ON pm.plan_id = mp.id
               WHERE pm.id = ? AND mp.user_id = ?""",
            (meal_id, user_id)
        )
        if not await cursor.fetchone():
            return None
        
        # Build update query
        updates = []
        params = []
        
        if recipe_id is not None:
            updates.append("recipe_id = ?")
            params.append(recipe_id)
        if date is not None:
            updates.append("date = ?")
            params.append(date)
        if meal_type is not None:
            updates.append("meal_type = ?")
            params.append(meal_type)
        if servings is not None:
            updates.append("servings = ?")
            params.append(servings)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        
        if updates:
            params.append(meal_id)
            query = f"UPDATE planned_meals SET {', '.join(updates)} WHERE id = ?"
            await db.execute(query, params)
            await db.commit()
        
        # Return updated meal
        cursor = await db.execute(
            """SELECT pm.*, sr.dish_name, sr.analysis_json 
               FROM planned_meals pm 
               LEFT JOIN saved_recipes sr ON pm.recipe_id = sr.id
               WHERE pm.id = ?""",
            (meal_id,)
        )
        row = await cursor.fetchone()
        
        if row:
            meal = dict(row)
            if meal.get("analysis_json"):
                meal["analysis"] = json.loads(meal["analysis_json"])
                del meal["analysis_json"]
            return meal
        return None


async def delete_planned_meal(meal_id: int, user_id: str) -> bool:
    """Delete a planned meal"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Verify meal belongs to user's plan
        cursor = await db.execute(
            """SELECT pm.id FROM planned_meals pm
               JOIN meal_plans mp ON pm.plan_id = mp.id
               WHERE pm.id = ? AND mp.user_id = ?""",
            (meal_id, user_id)
        )
        if not await cursor.fetchone():
            return False
        
        await db.execute("DELETE FROM planned_meals WHERE id = ?", (meal_id,))
        await db.commit()
        return True


async def get_week_recipes(plan_id: str, user_id: str) -> List[dict]:
    """Get all recipes from a meal plan for shopping list generation"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            """SELECT DISTINCT sr.id, sr.dish_name, sr.recipe_text
               FROM planned_meals pm
               JOIN meal_plans mp ON pm.plan_id = mp.id
               JOIN saved_recipes sr ON pm.recipe_id = sr.id
               WHERE pm.plan_id = ? AND mp.user_id = ?""",
            (plan_id, user_id)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


# Barcode cache functions
async def get_barcode_cache(barcode: str) -> Optional[dict]:
    """Get cached barcode data"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        cursor = await db.execute(
            "SELECT * FROM barcode_cache WHERE barcode = ?",
            (barcode,)
        )
        row = await cursor.fetchone()
        
        if row:
            return {
                "barcode": row["barcode"],
                "product_data": json.loads(row["product_data"]),
                "cached_at": row["cached_at"]
            }
        return None


async def set_barcode_cache(barcode: str, product_data: dict) -> None:
    """Cache barcode data"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT OR REPLACE INTO barcode_cache (barcode, product_data, cached_at)
               VALUES (?, ?, CURRENT_TIMESTAMP)""",
            (barcode, json.dumps(product_data))
        )
        await db.commit()


# Refresh token functions
async def store_refresh_token(jti: str, user_id: str, expires_at: str) -> None:
    """Store a refresh token in the database"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT INTO refresh_tokens (jti, user_id, expires_at)
               VALUES (?, ?, ?)""",
            (jti, user_id, expires_at)
        )
        await db.commit()


async def get_refresh_token(jti: str) -> Optional[dict]:
    """Get a refresh token by its JTI"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM refresh_tokens WHERE jti = ?",
            (jti,)
        )
        row = await cursor.fetchone()
        if row:
            return dict(row)
        return None


async def delete_refresh_token(jti: str) -> bool:
    """Delete a refresh token (used during token rotation)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM refresh_tokens WHERE jti = ?",
            (jti,)
        )
        await db.commit()
        return cursor.rowcount > 0


async def delete_user_refresh_tokens(user_id: str) -> None:
    """Delete all refresh tokens for a user (used during logout)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "DELETE FROM refresh_tokens WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


# Token blacklist functions
async def blacklist_token(jti: str, token_type: str, expires_at: str) -> None:
    """Add a token to the blacklist"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """INSERT OR IGNORE INTO blacklisted_tokens (jti, token_type, expires_at)
               VALUES (?, ?, ?)""",
            (jti, token_type, expires_at)
        )
        await db.commit()


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute(
            "SELECT jti FROM blacklisted_tokens WHERE jti = ?",
            (jti,)
        )
        row = await cursor.fetchone()
        return row is not None


async def cleanup_expired_tokens() -> None:
    """Remove expired tokens from refresh_tokens and blacklisted_tokens tables"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Clean up expired refresh tokens
        await db.execute(
            "DELETE FROM refresh_tokens WHERE expires_at < CURRENT_TIMESTAMP"
        )
        # Clean up expired blacklisted tokens (no longer need to track them)
        await db.execute(
            "DELETE FROM blacklisted_tokens WHERE expires_at < CURRENT_TIMESTAMP"
        )
        await db.commit()