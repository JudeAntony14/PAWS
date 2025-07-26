import signal
import sys
import time
from datetime import datetime
from pathlib import Path
import logging
from RFQsClassifier import RFQsProcessor
from RFQcomposer import RFQComposer
from QuotationClassifier import QuotationProcessor

class WorkflowManager:
    def __init__(self):
        # Initialize processors
        self.rfq_classifier = RFQsProcessor()
        self.rfq_composer = RFQComposer()
        self.quotation_processor = QuotationProcessor()
        
        # Setup logging
        self.logger = logging.getLogger('WorkflowManager')
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        handler = logging.FileHandler('workflow_manager.log')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        # Add handler if it doesn't exist
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        self.running = True
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("Received shutdown signal. Cleaning up...")
        self.running = False

    def cleanup(self):
        """Perform cleanup operations"""
        self.logger.info("Performing cleanup operations...")
        # Add any specific cleanup tasks here
        self.logger.info("Cleanup complete")

    def get_time_window(self):
        """Return test settings with very short intervals"""
        return {
            'window': 'testing',
            'check_interval': 0.5,  # 0.5 seconds between cycles
            'process_gap': 0.2,     # 0.2 seconds between processes
            'cycle_gap': 0.5        # minimum 0.5 seconds between cycles
        }

    def run_cycle(self, process_gap):
        """Run one complete cycle of all processes"""
        try:
            # RFQ Classifier
            self.logger.info("Starting RFQ classification...")
            self.rfq_classifier.process_emails()
            time.sleep(process_gap)
            
            # RFQ Composer
            self.logger.info("Starting RFQ composition...")
            self.rfq_composer.process_all_rfqs()
            time.sleep(process_gap)
            
            # Quotation Classifier
            self.logger.info("Starting quotation processing...")
            self.quotation_processor.process_emails()
            
        except Exception as e:
            self.logger.error(f"Error in processing cycle: {str(e)}")

    def run(self):
        """Main workflow loop"""
        self.logger.info("Starting workflow manager (TEST MODE - Fixed Intervals)...")
        
        try:
            while self.running:
                try:
                    # Run the cycle
                    cycle_start = time.time()
                    self.run_cycle(0.2)  # Fixed 0.2s between processes
                    cycle_duration = time.time() - cycle_start
                    
                    # Fixed 0.5s between cycles, regardless of duration
                    self.logger.info(
                        f"Cycle completed in {cycle_duration:.2f}s. "
                        f"Waiting fixed 0.5s before next cycle"
                    )
                    
                    # Break sleep into smaller intervals to check running status
                    remaining_sleep = 0.5  # Fixed 0.5s between cycles
                    while remaining_sleep > 0 and self.running:
                        sleep_chunk = min(0.1, remaining_sleep)  # Sleep in 0.1s chunks
                        time.sleep(sleep_chunk)
                        remaining_sleep -= sleep_chunk
                        
                except Exception as e:
                    self.logger.error(f"Error in workflow loop: {str(e)}")
                    # Sleep for 1 second before retrying on error
                    time.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"Critical error in workflow manager: {str(e)}")
        finally:
            self.cleanup()
            self.logger.info("Workflow manager stopped")

def main():
    manager = WorkflowManager()
    manager.run()

if __name__ == "__main__":
    main() 