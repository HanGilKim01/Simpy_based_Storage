from base_Job import Job
from config_SimPy import *
from specialized_Process import Proc_Build, Proc_Wash, Proc_Dry, Proc_Inspect
from base_Customer import OrderReceiver


class Manager(OrderReceiver):
    """
    Manager class to control the manufacturing processes and track orders

    Attributes:
        env (simpy.Environment): Simulation environment
        logger (Logger): Logger object for logging events
        next_job_id (int): Next job ID counter
        completed_orders (list): List of completed orders 
    """

    def __init__(self, env, logger=None):
        self.env = env
        self.logger = logger

        # Next job ID counter
        self.next_job_id = 1

 

        # Tracking completed jobs and orders
        self.completed_orders = []

        # When calling setup_processes, the manager (self) itself is also passed as an argument
        self.setup_processes(manager=self)
        #이는 공정 설정 과정에서 Manager 객체를 필요로 하거나, 공정들 사이의 상호 연결을 위해 Manager를 참조하도록 설계되었음을 의미합니다.

    def setup_processes(self, manager=None):
        """Create and connect all manufacturing processes"""
        # Create processes
        self.proc_build = Proc_Build(self.env, self.logger)
        self.proc_wash = Proc_Wash(self.env, self.logger)
        self.proc_dry = Proc_Dry(self.env, self.logger)
        self.proc_inspect = Proc_Inspect(self.env, manager, self.logger)

        # Connect processes
        self.proc_build.connect_to_next_process(self.proc_wash)
        self.proc_wash.connect_to_next_process(self.proc_dry)
        self.proc_dry.connect_to_next_process(self.proc_inspect)

        if self.logger:
            self.logger.log_event(
                "Manager", "Manufacturing processes created and connected")

    def receive_order(self, order):
        """Process incoming order from Customer"""
        if self.logger:
            self.logger.log_event(
                "Order", f"Received Order {order.id_order} with {order.num_patients} patients")

        # Mark order start time
        order.time_start = self.env.now

        # Convert order to jobs based on policy
        self.create_jobs_for_proc_build(order)

        return order

    def create_jobs_for_proc_build(self, order):
        """Convert Order to Jobs based on POLICY_ORDER_TO_JOB"""
        all_patients = order.list_patients

        for patient in all_patients:
            patient_items = patient.list_items

            # If patient's items fit within PALLET_SIZE_LIMIT, create a single job
            if len(patient_items) <= PALLET_SIZE_LIMIT:
                # Create a job with all items from this patient
                job = Job(self.next_job_id, patient_items)
                self.next_job_id += 1

                # Send job to Build process
                if self.logger:
                    self.logger.log_event(
                        "Manager", f"Created job {job.id_job} for patient {patient.id_patient} with {len(patient_items)} items")
                self.proc_build.add_to_queue(job)
            else:
                # Patient's items exceed PALLET_SIZE_LIMIT, apply splitting policy
                if POLICY_ORDER_TO_JOB == "MAX_PER_JOB":
                    # Split items into multiple jobs of roughly equal size
                    items_per_job = PALLET_SIZE_LIMIT
                    for i in range(0, len(patient_items), items_per_job):
                        job_items = patient_items[i:i+items_per_job]
                        job = Job(self.next_job_id, job_items)
                        self.next_job_id += 1

                        # Send job to Build process
                        if self.logger:
                            self.logger.log_event(
                                "Manager", f"Created job {job.id_job} for patient {patient.id_patient} with {len(job_items)} items (split job)")
                        self.proc_build.add_to_queue(job)

                # Additional policies can be implemented here if needed

    def create_job_for_defects(self):
        """Create jobs for defective items that need rework"""
        # Get defective items from inspection process
        defective_items = self.proc_inspect.defective_items

        if not defective_items:
            return

        # Log the number of defective items found
        # if self.logger:
        #     self.logger.log_event(
        #         "Manager", f"Found {len(defective_items)} defective items to process")

        # Check if we have enough defective items for a job
        if len(defective_items) >= POLICY_NUM_DEFECT_PER_JOB:
            # Take the specified number of defective items
            items_for_job = defective_items[:POLICY_NUM_DEFECT_PER_JOB]

            # Create a new job for these defective items
            job = Job(self.next_job_id, items_for_job)
            job.is_reprocess = True  # Mark as a rework job
            self.next_job_id += 1

            # Remove these items from the defective items list
            self.proc_inspect.defective_items = defective_items[POLICY_NUM_DEFECT_PER_JOB:]

            # Add the job to the Build process queue according to policy
            if POLICY_REPROC_SEQ_IN_QUEUE == "QUEUE_LAST":
                # Add job to the end of the queue
                self.proc_build.add_to_queue(job)
                if self.logger:
                    self.logger.log_event(
                        "Manager", f"Created rework job {job.id_job} with {len(items_for_job)} defective items (added to end of queue)")
                    self.logger.log_event(
                        "Manager", f"Remaining defective items: {len(self.proc_inspect.defective_items)}")

    def get_processes(self):
        """Return processes as a dictionary for statistics collection"""
        return {
            'build': self.proc_build,
            'wash': self.proc_wash,
            'dry': self.proc_dry,
            'inspect': self.proc_inspect
        }

    def collect_statistics(self):
        """Collect basic statistics from processes"""
        stats = {}

        # Completed jobs per process
        # 각 공정(빌드, 워시, 드라이, 인스펙트)의 completed_jobs 리스트의 길이를 계산하여, 해당 공정에서 완료된 작업의 총 개수를 저장합니다.
        stats['build_completed'] = len(self.proc_build.completed_jobs)
        stats['wash_completed'] = len(self.proc_wash.completed_jobs)
        stats['dry_completed'] = len(self.proc_dry.completed_jobs)
        stats['inspect_completed'] = len(self.proc_inspect.completed_jobs)

        # Queue sizes
        # 각 공정의 작업 큐(Stack)의 크기(size 프로퍼티)를 조회하여, 현재 대기 중인 작업의 수를 저장합니다.
        stats['build_queue'] = self.proc_build.job_store.size
        stats['wash_queue'] = self.proc_wash.job_store.size
        stats['dry_queue'] = self.proc_dry.job_store.size
        stats['inspect_queue'] = self.proc_inspect.job_store.size

        # Defective items
        # 검사(Inspect) 공정에서 관리되는 불량 항목 리스트(defective_items)의 길이를 계산하여, 현재 남아있는 불량 항목의 수를 저장합니다.
        stats['defective_items'] = len(self.proc_inspect.defective_items)

        return stats
