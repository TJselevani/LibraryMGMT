# controllers/book_categories_controller.py
from sqlalchemy.exc import IntegrityError
from db.models import BookCategory, Audience
from typing import List, Optional, Dict, Any
import re


class BookCategoriesController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self) -> List[BookCategory]:
        """Get all book categories"""
        try:
            with self.db_manager.get_session() as session:
                return session.query(BookCategory).order_by(BookCategory.name).all()
        except IntegrityError:
            return {
                "success": False,
                "message": "Book with this accession number already exists",
            }
        except Exception as e:
            return {"success": False, "message": f"Error fetching categories: {str(e)}"}

    def get_by_id(self, category_id: int) -> Optional[BookCategory]:
        """Get a book category by ID"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BookCategory)
                .filter(BookCategory.id == category_id)
                .first()
            )

    def get_by_name(self, name: str) -> Optional[BookCategory]:
        """Get a book category by name"""
        with self.db_manager.get_session() as session:
            return session.query(BookCategory).filter(BookCategory.name == name).first()

    def get_by_audience(self, audience: Audience) -> List[BookCategory]:
        """Get categories by audience type"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BookCategory)
                .filter(BookCategory.audience == audience)
                .all()
            )

    def create(
        self, name: str, audience: Audience, color_code: str = None
    ) -> BookCategory:
        """Create a new book category"""
        if color_code:
            color_code = self._validate_and_format_colors(color_code)

        category = BookCategory(name=name, audience=audience, color_code=color_code)

        with self.db_manager.get_session() as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category

    def update(self, category_id: int, **kwargs) -> Optional[BookCategory]:
        """Update a book category"""
        with self.db_manager.get_session() as session:
            category = (
                session.query(BookCategory)
                .filter(BookCategory.id == category_id)
                .first()
            )
            if not category:
                return None

            if "color_code" in kwargs and kwargs["color_code"]:
                kwargs["color_code"] = self._validate_and_format_colors(
                    kwargs["color_code"]
                )

            for key, value in kwargs.items():
                if hasattr(category, key):
                    setattr(category, key, value)

            session.commit()
            session.refresh(category)
            return category

    def delete(self, category_id: int) -> bool:
        """Delete a book category"""
        with self.db_manager.get_session() as session:
            category = (
                session.query(BookCategory)
                .filter(BookCategory.id == category_id)
                .first()
            )
            if not category:
                return False

            session.delete(category)
            session.commit()
            return True

    def get_categories_with_color_info(self) -> List[Dict[str, Any]]:
        """Get categories with parsed color information"""
        categories = self.get_all()
        result = []

        for category in categories:
            colors = self._parse_color_codes(category.color_code)
            result.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "audience": category.audience,
                    "color_code": category.color_code,
                    "colors": colors,
                    "color_count": len(colors),
                    "primary_color": colors[0] if colors else None,
                    "secondary_color": colors[1] if len(colors) > 1 else None,
                    "created_at": category.created_at,
                    "updated_at": category.updated_at,
                }
            )

        return result

    def _validate_and_format_colors(self, color_code: str) -> str:
        """Validate and format color codes"""
        if not color_code:
            return None

        colors = re.split(r"[,/\s]+", color_code.strip())
        valid_colors = []

        for color in colors:
            color = color.strip().upper()
            if color and self._is_valid_color(color):
                valid_colors.append(color)

        return " / ".join(valid_colors) if valid_colors else None

    def _is_valid_color(self, color: str) -> bool:
        """Validate if a color name/code is valid"""
        if re.match(r"^#[0-9A-Fa-f]{6}$", color):
            return True

        valid_color_names = {
            "RED",
            "GREEN",
            "BLUE",
            "YELLOW",
            "ORANGE",
            "PURPLE",
            "PINK",
            "BROWN",
            "BLACK",
            "WHITE",
            "GRAY",
            "GREY",
            "LAVENDER",
            "TURQUOISE",
            "CYAN",
            "MAGENTA",
            "LIME",
            "MAROON",
            "NAVY",
            "OLIVE",
            "SILVER",
            "TEAL",
            "AQUA",
            "FUCHSIA",
            "GOLD",
            "INDIGO",
            "KHAKI",
            "CORAL",
            "SALMON",
            "VIOLET",
            "CRIMSON",
            "AZURE",
            "BEIGE",
            "TAN",
        }

        return color in valid_color_names

    def _parse_color_codes(self, color_code: str) -> List[str]:
        """Parse color codes into individual colors"""
        if not color_code:
            return []
        colors = re.split(r"[,/\s]+", color_code.strip())
        return [color.strip() for color in colors if color.strip()]

    def get_color_statistics(self) -> Dict[str, Any]:
        """Get statistics about color usage"""
        categories = self.get_categories_with_color_info()

        color_counts = {}
        audience_colors = {}
        total_with_colors = 0
        total_without_colors = 0

        for cat in categories:
            if cat["colors"]:
                total_with_colors += 1
                for color in cat["colors"]:
                    color_counts[color] = color_counts.get(color, 0) + 1
            else:
                total_without_colors += 1

            audience = (
                cat["audience"].value
                if hasattr(cat["audience"], "value")
                else str(cat["audience"])
            )
            if audience not in audience_colors:
                audience_colors[audience] = {"with_colors": 0, "without_colors": 0}

            if cat["colors"]:
                audience_colors[audience]["with_colors"] += 1
            else:
                audience_colors[audience]["without_colors"] += 1

        return {
            "total_categories": len(categories),
            "total_with_colors": total_with_colors,
            "total_without_colors": total_without_colors,
            "most_used_colors": sorted(
                color_counts.items(), key=lambda x: x[1], reverse=True
            ),
            "audience_breakdown": audience_colors,
        }

    def bulk_create_default_categories(self):
        """Create default book categories with colors"""
        default_categories = [
            {
                "name": "ABC / 123 / Basic Concept",
                "audience": Audience.CHILDREN,
                "color_code": "GREEN / LAVENDER",
            },
            {"name": "Adventure", "audience": Audience.CHILDREN, "color_code": "RED"},
            {"name": "Animals", "audience": Audience.CHILDREN, "color_code": "BLUE"},
            {
                "name": "Arts / Music / Dance",
                "audience": Audience.CHILDREN,
                "color_code": "GREEN / ORANGE",
            },
            {
                "name": "Cars / Trucks",
                "audience": Audience.CHILDREN,
                "color_code": "ORANGE / RED",
            },
            {
                "name": "Dinosaurs",
                "audience": Audience.CHILDREN,
                "color_code": "ORANGE / BLUE",
            },
            {"name": "Fiction", "audience": Audience.ADULT, "color_code": None},
            {"name": "Non-Fiction", "audience": Audience.ADULT, "color_code": None},
            {"name": "Biography", "audience": Audience.ADULT, "color_code": "PURPLE"},
            {
                "name": "Science Fiction",
                "audience": Audience.YOUNG_ADULT,
                "color_code": "SILVER / BLUE",
            },
            {"name": "Romance", "audience": Audience.YOUNG_ADULT, "color_code": "PINK"},
            {
                "name": "Mystery / Thriller",
                "audience": Audience.ADULT,
                "color_code": "BLACK / RED",
            },
        ]

        created_count = 0
        for cat_data in default_categories:
            existing = self.get_by_name(cat_data["name"])
            if not existing:
                try:
                    self.create(
                        name=cat_data["name"],
                        audience=cat_data["audience"],
                        color_code=cat_data["color_code"],
                    )
                    created_count += 1
                except Exception as e:
                    print(f"Error creating category {cat_data['name']}: {e}")

        return created_count
