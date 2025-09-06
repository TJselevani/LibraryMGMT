class IntegrationHelper:
    """Helper class to integrate analytics into existing HomeView"""

    @staticmethod
    def patch_homeview(homeview_instance):
        """
        Patches an existing HomeView instance with analytics functionality
        Call this after creating your HomeView instance
        """
        import types

        # Add the new methods to the existing instance
        homeview_instance._build_bottom_layout_with_analytics = types.MethodType(
            homeview_instance._build_bottom_layout_with_analytics, homeview_instance
        )
        homeview_instance._get_recent_activities = types.MethodType(
            homeview_instance._get_recent_activities, homeview_instance
        )

        # Replace the original method
        homeview_instance._build_bottom_layout = (
            homeview_instance._build_bottom_layout_with_analytics
        )

        print("HomeView successfully patched with analytics functionality!")

        return homeview_instance

    @staticmethod
    def check_dependencies():
        """Check if required dependencies are available"""
        required_packages = {
            "PyQt5.QtWebEngineWidgets": "QWebEngineView",
            "plotly": "plotly",
        }

        missing_packages = []

        for package, component in required_packages.items():
            try:
                __import__(package)
                print(f"✓ {component} available")
            except ImportError:
                missing_packages.append(package)
                print(f"✗ {component} missing")

        if missing_packages:
            print("\nTo install missing packages run:")
            print("pip install PyQtWebEngine plotly")
            return False

        return True
