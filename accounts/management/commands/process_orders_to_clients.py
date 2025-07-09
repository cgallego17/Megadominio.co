from django.core.management.base import BaseCommand
from accounts.views import process_existing_orders_to_clients
from django.db import transaction

class Command(BaseCommand):
    help = 'Procesa órdenes existentes completadas para crear clientes automáticamente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin hacer cambios reales (solo mostrar qué se haría)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando procesamiento de órdenes a clientes...')
        )
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING('MODO DRY-RUN: No se harán cambios reales')
            )
        
        try:
            with transaction.atomic():
                result = process_existing_orders_to_clients()
                
                if result:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Procesamiento completado:\n'
                            f'- Clientes creados: {result["created"]}\n'
                            f'- Clientes actualizados: {result["updated"]}\n'
                            f'- Total procesado: {result["total_processed"]}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Error en el procesamiento')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error durante el procesamiento: {e}')
            ) 