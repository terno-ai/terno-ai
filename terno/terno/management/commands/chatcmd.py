from django.core.management.base import BaseCommand
import terno.models as models
import terno.utils as utils
from django.contrib.auth.models import User
from terno.agent.spider_agent.agent import PromptAgent
from terno.agent.spider_agent.env import TernoShieldEnv
from terno.llm import LLMFactory

        

class Command(BaseCommand):
    help = 'My custom Django management command'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Name of the person to greet')

    def handle(self, *args, **options):
        datasource = models.DataSource.objects.get(
            id=1,
            enabled=True)
        login_string = 'admin'
        user = User.objects.get(username=login_string)
        roles = user.groups.values_list('name', flat=True)

        mDB = utils.prepare_mdb(datasource, roles)
        schema_generated = mDB.generate_schema()

        agent = PromptAgent()
        env = TernoShieldEnv(datasource, mDB)
        organisation = models.Organisation.objects.get(id=1)
        llm, is_default_llm = LLMFactory.create_llm(organisation)
        
        while True:
            question = input("Your question: ")
            agent.set_env_and_task(env=env, task=question, llm=llm)
            done, result_output = agent.run()
            
        self.stdout.write(self.style.SUCCESS(f'Hello, {name}!'))

