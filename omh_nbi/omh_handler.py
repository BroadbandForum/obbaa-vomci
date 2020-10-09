# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Base class for all OMH handlers.
# Executes a sequence of OMCI transactions until completion or failure.
# Supports foreground and background execution.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" The base class for OMH handlers implementing OMCI sequences for different scenarios
"""
from omci_types import Name, RawMessage, AutoGetter
from omci_logger import OmciLogger
from database.omci_me_types import omci_status
from encode_decode.omci_action import OmciAction
from enum import Enum, auto
import threading
from time import time

logger = OmciLogger.getLogger(__name__)

class OMHStatus(Enum):
    """ OMH Handler completion status """
    OK = auto()
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    CANCELED = auto()
    COMMUNICATION_ERROR = auto()
    TIMEOUT = auto()
    NOT_SUPPORTED = auto()
    ENCODING_DECODING_ERROR = auto()
    ERROR_REPORTED_BY_ONU = auto()
    INTERNAL_ERROR = auto()
    ERROR_IN_PARAMETERS = auto()
    NO_RESOURCES = auto()
    OLT_NOT_FOUND = auto()
    ONU_NOT_FOUND = auto()

class OmhHandler(Name, AutoGetter):
    """ OmhHandler base class. Thius class is never used by itself.
        Derived classes must define 'run_to_completion' function that runs the
        entire OMH handler to completion in caller's context
    """

    def __init__(self, name: str, onu: 'OnuDriver', description: str = None):
        """`!OmhHandler` constructor.
        Args:
            name: OMH handler name. This is only used for documentation purposes.
            description: OMH handler description. This is only used for
                documentation purposes.
            onu: OnuDriver instance
        """
        super().__init__(name, description)
        self._onu = onu
        self._thread = None
        self._notify_done = None
        self._status = OMHStatus.NOT_STARTED
        self._transaction_status = OMHStatus.NOT_STARTED
        self._canceled = False
        self._transaction_sem = threading.Semaphore(0)
        self._start_time = self._stop_time = 0.0
        self._actions = []
        self._action_waiting_for_response = None
        self._running = False
        self._rolling_back = False
        self._num_messages = 0
        self._num_transactions = 0
        self._num_retries = 0
        self._top_level = True
        self._user_data = None

    def __del__(self):
        if self._thread is not None and self._thread is not threading. current_thread():
            self._thread.join()

    @property
    def status(self) -> OMHStatus:
        """ Get OMH handler status """
        return self._status

    @property
    def num_transactions(self) -> int:
        """ Get the number of transactions executed by the OMH handler """
        return self._num_transactions

    @property
    def num_messages(self) -> int:
        """ Get number of messages sent by the OMH handler """
        return self._num_transactions

    @property
    def num_retries(self) -> int:
        """ Get the number of times OMCI message had to be retransmitted """
        return self._num_retries

    @property
    def user_data(self):
        return self._user_data

    def set_user_data(self, user_data):
        self._user_data = user_data

    def stats(self) -> str:
        """ Get statistics string """
        return 'transactions:{} messages:{} retries:{}'.format(
            self._num_transactions, self._num_messages, self._num_retries)

    def duration(self) -> float:
        """ Returns:
                execution time (s)
        """
        stop_time = self._stop_time != 0.0 and self._stop_time or time()
        return self._start_time == 0.0 and 0.0 or stop_time - self._start_time

    def _run_to_completion(self):
        logger.info("Starting OMH handler '{}' for ONU '{}'".format(self.name, self._onu.onu_id))
        self._start_time = time()
        self._status = self.run_to_completion()
        self._stop_time = time()
        logger.info("OMH handler '{}' for ONU '{}' finished with status {}. Run time {:.3f}s. {}".format(
            self.name, self._onu.onu_id, self._status, self.duration(), self.stats()))
        # If success - commit changes to the main MIB, otherwise - rollback
        if self._top_level:
            if self._status == OMHStatus.OK:
                self._onu.commit()
            else:
                self.rollback()
            self._actions.clear()
        # Make sure to clear pending requests belonging to this OMH handler, if any
        self._onu.remove_pending(self)

    def _thread_function(self):
        self._run_to_completion()
        self._running = False
        self._notify_done(self)

    def _start(self, notify_done = None) -> OMHStatus:
        """ Internal function. Start the OMH handler in the foreground or in the background.

        Args:
            notify_done: Optional OMH handler completed notification handler.<br>
                If notify_done is None (default), the function blocks until OMH handler execution
                is completed.<br>
                If notify_done is set, the 'start' function spawns a new thread.
                The thread is terminated when the OMH handler is finished. notify_done(this_handler)
                is called to inform the requester that OMH handler has completed.
        Returns:
            self.completion_status
        """
        if self._running:
            logger.warning("OMH handler {} is already running".format(self._name))
            return OMHStatus.IN_PROGRESS

        self._running = True
        self._canceled = False
        if notify_done is not None:
            self._thread = threading.Thread(name=self.name, target=self._thread_function)
            self._status = OMHStatus.IN_PROGRESS
            self._notify_done = notify_done
            self._thread.start()
        else:
            self._run_to_completion()
            self._running = False
        return self._status

    def start(self, notify_done) -> OMHStatus:
        """ Start the OMH handler in the background.

        This function spawns a new thread and executes the OMH handler to completion
        in this dedicated thread's context.

        Args:
            notify_done: OMH handler completed notification handler.
                         notify_done(this_handler) is called upon completion and the
                         background thread is destroyed.
        Returns:
            self.completion_status
        """
        return self._start(notify_done)

    def run(self) -> OMHStatus:
        """ Start the OMH handler and run it to completion.

        Returns:
            self.completion_status
        """
        return self._start()

    def wait_for_completion(self) -> OMHStatus:
        """ Wait for completion of an OMH handler running in its own thread """
        if self._thread is None:
            return self._status
        self._thread.join()
        self._thread = None

    def cancel(self):
        """ Cancel running OMH handler """
        self._canceled = True

    def run_subsidiary(self, subsidiary: 'OmhHandler') -> OMHStatus:
        """ Execute a subsidiary OMH handler in the context of the 'self' OMH handler.

        Args:
            subsidiary : subsidiary OMH handler to run to completion
        Returns:
            subsidiary OMH handler completion status
        """
        subsidiary._top_level = False
        self._status = subsidiary.run()
        self._num_transactions += subsidiary._num_transactions
        self._num_messages += subsidiary._num_messages
        self._num_retries += subsidiary._num_retries
        self._actions += subsidiary._actions
        return self._status

    def transaction(self, action : OmciAction = None) ->  OMHStatus:
        """ Perform request-response transaction.

        The transaction can involve multiple request-response exchanges if
        action has to be split to fit in a BASELINE OMCI message.

        Args:
              action : Action to execute. In most cases this parameter is set (not None).
                       It might be None only if the previous transaction has to be continued
                       with the same ME, for example, for get-next or mib-upload-next
        Returns:
                Transaction completion status
        """
        assert action is not None or len(self._actions) > 0
        if self._canceled:
            return OMHStatus.CANCELED
        self._transaction_status = OMHStatus.IN_PROGRESS
        if action is None:
            action = self._actions[-1]
        elif not self._rolling_back:
            self._actions.append(action)
        self._num_transactions += 1
        # Loop by (request,response) message pairs
        while True:
            # Convert to raw OMCI message
            self._num_messages += 1
            raw_msg = action.encode(self._onu.next_tci)
            if raw_msg is None:
                self._transaction_status = OMHStatus.ENCODING_DECODING_ERROR
                break

            self._action_waiting_for_response = action.ar and action or None

            # Transmit and wait for acknowledge loop
            num_retries = 0
            while True:
                # Send request to ONU
                if not self._onu.send(self, raw_msg, action.ar, action.tci):
                    self._transaction_status = OMHStatus.COMMUNICATION_ERROR
                    self._action_waiting_for_response = None
                    break

                # Wait for response if necessary
                if not action.ar:
                    break
                if self._transaction_sem.acquire(True, self._onu.ack_timeout):
                    break   # All good

                # Timeout. Need to retry
                num_retries += 1
                if num_retries > self._onu.max_retries:
                    self._transaction_status = OMHStatus.TIMEOUT
                    break
                self._num_retries += 1
                action.reinit()

            # Couldn't send or out of retries?
            if self._transaction_status != OMHStatus.IN_PROGRESS:
                break

            # OMCI error?
            if action.omci_result != 0 and action.omci_result != omci_status['ATTRIBUTES_FAILED_OR_UNKNOWN']:
                self._transaction_status = OMHStatus.ERROR_REPORTED_BY_ONU
                break

            # Increment local mib_sync if necessary (decided by the action)
            if action.is_configuration:
                self._onu.increment_mib_sync()

            # Do the next iteration if action was split
            if action.remaining_attr_mask == 0:
                self._transaction_status = OMHStatus.OK
                break

            # Prepare action for the next iteration
            action.reinit()

        # Commit to the candidate MIB if successful
        if self._transaction_status == OMHStatus.OK and not self._rolling_back:
            action.commit(self._onu)

        return self._transaction_status

    @property
    def last_action(self) -> OmciAction:
        """ Get the last action executed by the OMH handler """
        return self._actions[-1]

    def recv(self, msg: RawMessage):
        """
        This function is called by OnuDriver when an Ack
        for an outstanding request is received.

        Args:
            msg: raw OMCI message
        """
        if self._action_waiting_for_response is None:
            logger.warning("Unexpected response from ONU {}. Ignored.".format(self._onu.onu_id))
            return

        # Unlock pending transaction if decoded successfully
        if  OmciAction.decode(msg, self._action_waiting_for_response) is not None:
            self._action_waiting_for_response = None
            self._transaction_sem.release()

    def rollback(self):
        """ Rollback all handlers performed by the OMH handler.

        Returns: rollback status
        """
        # Rollback in the order opposite to execution
        self._onu.clear_candidate()
        self._rolling_back = True
        self._actions.reverse()
        for action in self._actions:
            rollback_action = action.rollback(self._onu)
            if rollback_action is not None:
                rollback_status = self.transaction(rollback_action)
                if rollback_status == OMHStatus.TIMEOUT or rollback_status == OMHStatus.COMMUNICATION_ERROR:
                    break
        self._rolling_back = False

    def logerr_and_return(self, status: OMHStatus, text: str) -> OMHStatus:
        """ Log error and return the error status.

        Args:
            status: OMH handler completion status
            text: Error text
        Returns: status
        """
        logger.warning('ONU {}: {}: {}'.format(self._onu.onu_id, status.name, text))
        return status
