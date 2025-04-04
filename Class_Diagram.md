```mermaid
classDiagram
    
    class Item {
    + id_order : int
    + id_patient : int
    + id_item : int
    + type_item : "aligner"
    + is_completed : bool
    + is_defect : bool

    }

    class Patient {
    + id_order : int
    + id_patient : int
    + num_items : int
    + list_items : list
    + is_completed : bool
    + item_counter : int
    + _create_items_for_patient(id_order, id_patient, num_items)
    + _get_next_item_id()
    + check_completion()
    }

    class Order {
    + id_order : int
    + num_patients : int
    + list_patients : list
    + due_date : int
    + time_start : None
    + time_end : None
    + patient_counter : int
    + _create_patients_for_order(id_order, num_patients)
    + _get_next_patient_id()
    + check_completion()
    }
    
    class Customer {
    + env : simpy.environment
    + logger : list
    + order_counter : int
    + get_next_order_id()
    + create_order()
    + send_order()
    }


    class Job {
    + id_job : int
    + workstation : dict
    + list_items : list
    + time_processing_start : None
    + time_processing_end : None
    + time_waiting_start : None
    + time_waiting_end : None
    + is_reprocess : bool
    + processing_history : list
    }

    class Stack {
    + name : str
    + queue_length_history : list
    + put(item)
    + get()
    + is_empty()
    + size()
    }

    class Process {
    + name_process : str
    + env : simpy.environment
    + logger : list
    + list_processors : list
    + job_store : Stack()
    + processor_resources : dict
    + complted_jobs : list
    + next_process : None
    + resource_trigger : env.event()
    + job_added_trigger : env.event()
    + process : env.process()
    + connect_to_next_process(next_process)
    + register_processor(processor)
    + add_to_queue(job)
    + run()
    + seize_resources()
    + delay_resources(processor_resource, jobs)
    + release_resources(processor_resource, request)
    + create_process_step(job, processor_resource)
    + send_job_to_next(job)
    }

    class Worker {
    + type_processor : str
    + id_worker : int
    + name_worker : str
    + available_status : bool
    + working_job : None
    + processing_time : int
    + busy_time : int
    + last_status_change : int
    }

    class Machine {
    + type_processor : str
    + id_machine : int
    + name_process : str
    + name_machine : str
    + available_status : bool
    + list_working_job : list
    + capacity_jobs : int
    + processing_time : int
    + busy_time : int
    + last_status_change : int
    + allows_job_addition_during_processing : bool
    }

    class ProcessorResource {
    + processor_type : str
    + capacity : int
    + id : int
    + name : str
    + allows_job_addition_during_processing : bool
    + current_job : bool
    + current_jobs : list
    + processing_time : int
    + processing_started : bool
    + request(*args, **kwargs)
    + release(request)
    + is_available()
    + start_job(job)
    + get_jobs()
    + finish_jobs()
    }

    class Logger {
    + env : simpy.environment
    + event_logs : list
    + log_event(event_type, message)
    + collect_statistics(processes)
    + visualize_statistics(stats, processes)
    + visualize_process_statistics(stats, stat_type)
    + visualize_queue_lengths(processes)
    + visualize_gantt(processes)
    + get_all_resources(processes)
    + get_color_for_job(job_id)
    }

    class Manager {
    + env : simpy.environment
    + logger : list
    + next_job_id : int
    + completed_orders : list
    + setup_processes(manager)
    + receive_order(order)
    + create_jobs_for_proc_build(order)
    + create_job_for_defects()
    + get_processes()
    + collect_statistics()
    }

    class Proc_Build {
    + apply_special_processing(processor, jobs)
    }

    class Proc_Wash {
    }

    class Proc_Dry {
    }

    class Proc_Inspect {
    + defective_items : list
    + apply_special_processing(processor, jobs)
    }

    class Worker_Inspect {
    }

    class Mach_3DPrint {
    }

    class Mach_Wash {
    }

    class Mach_Dry {
    }

%%{init: {"class": {"diagramMarginX": 200, "diagramMarginY": 50, "boxMargin": 20, "boxTextMargin": 10}}}%%
    %% 관계 표현
    Process <|-- Proc_Build : Inheritance
    Process <|-- Proc_Wash : Inheritance
    Process <|-- Proc_Dry : Inheritance
    Process <|-- Proc_Inspect : Inheritance

    Item --> Patient : contain
    Patient --> Order : contain

    Customer --> Order : generate
    Customer --> Manager : send order

    Manager --> Job : Split Order into Job
    Manager --> Stack : send Job list
    Manager --> Proc_Build : create job for defects

    Process --> Stack : get Job list

    ProcessorResource --> Proc_Build : offer resource
    ProcessorResource --> Proc_Wash : offer resource
    ProcessorResource --> Proc_Dry : offer resource
    ProcessorResource --> Proc_Inspect : offer resource

    Worker --> ProcessorResource : contain
    Machine --> ProcessorResource : contain

    Worker_Inspect --|> Worker : Inheritance
    Mach_3DPrint --|> Machine : Inheritance
    Mach_Wash --|> Machine : Inheritance
    Mach_Dry --|> Machine : Inheritance
    