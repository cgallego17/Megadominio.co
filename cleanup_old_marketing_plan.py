import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'megadominio.settings')
django.setup()

from servicios.models import Servicio
from accounts.models import PurchasableService

def cleanup_old_marketing_plan():
    print("🧹 Limpiando plan residual 'Marketing Profesional'...")
    
    try:
        # Buscar el servicio de Optimización Web y SEO
        servicio = Servicio.objects.get(nombre="Optimización Web y SEO")
        
        # Buscar el plan residual "Marketing Profesional"
        try:
            old_plan = PurchasableService.objects.get(
                name="Marketing Profesional",
                home_service=servicio
            )
            
            print(f"⚠️  Plan residual encontrado: {old_plan.name}")
            print(f"   - Precio actual: ${old_plan.price_monthly}/mes")
            print(f"   - Slug: {old_plan.slug}")
            
            # Eliminar el plan residual
            old_plan.delete()
            print(f"✅ Plan residual 'Marketing Profesional' eliminado")
            
        except PurchasableService.DoesNotExist:
            print(f"✅ No se encontró plan residual 'Marketing Profesional'")
        
        # Mostrar estado final limpio
        print(f"\n📊 Planes finales del servicio SEO:")
        final_plans = PurchasableService.objects.filter(home_service=servicio).order_by('price_monthly')
        for i, plan in enumerate(final_plans, 1):
            monthly_formatted = f"${plan.price_monthly:,}" if plan.price_monthly else "N/A"
            annual_formatted = f"${plan.price_annual:,}" if plan.price_annual else "N/A"
            print(f"   {i}. {plan.name}: {monthly_formatted}/mes - {annual_formatted}/año")
        
        print(f"\n🎉 ¡Limpieza completada! Ahora tienes {final_plans.count()} planes SEO limpios.")
        
    except Servicio.DoesNotExist:
        print("❌ Servicio 'Optimización Web y SEO' no encontrado")
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    cleanup_old_marketing_plan() 