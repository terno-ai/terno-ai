import openai
from django.core.management.base import BaseCommand
from django.conf import settings

from terno.terno.llm.base import LLMFactory
from terno.terno.llm.cot.agents import PromptAgent
from terno.terno.llm.cot.env import TernoShieldEnv
from terno.terno.models import Organisation

class Command(BaseCommand):
    help = 'Implements a chain-of-thought reasoning process using OpenAI LLM.'

    def add_arguments(self, parser):
        parser.add_argument('orgid', type=int, help='ID of the organization')
        parser.add_argument('dbid', type=int, help='The id of the database')
        parser.add_argument('userid', type=int, help='User Id of user on whose behalf it is going to start')
        parser.add_argument('query', type=str, help='The query or question that you need an answer for.')
    def handle(self, *args, **kwargs):
        org_id = kwargs['orgid']
        db_id = kwargs['dbid']
        user_id = kwargs['userid']
        question = kwargs['query']

        organisation = Organisation.objects.get(id=org_id)
        agent = PromptAgent()
        env = TernoShieldEnv(db_id, user_id)
        llm = LLMFactory.create_llm(organisation)
        agent.set_env_and_task(env=env, task=question,llm=llm)
        done, result_output = agent.run()
        