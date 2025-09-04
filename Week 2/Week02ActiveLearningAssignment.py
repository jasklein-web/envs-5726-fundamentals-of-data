import statistics
import datetime

class PreySample:
    def __init__(self, full_species_name, delta13c_list, tissue_description, sample_date_utc):
        self.full_species_name = full_species_name
        self.delta13c_list = delta13c_list
        self.tissue_description = tissue_description
        self.sample_date_utc = sample_date_utc

    def get_common_name(self):
        name_parts = self.full_species_name.split(' (')
        common_name = name_parts[0]
        return common_name

    def get_scientific_name(self):
        name_parts = self.full_species_name.split(' (')
        #.rstrip removes the trailing characters from the right end of a string
        scientific_name = name_parts[1].rstrip(')')
        return scientific_name

    def get_average_delta13c(self):
        average_delta13c = statistics.mean(self.delta13c_list)
        return average_delta13c

    def get_tissue_count(self):
        tissue_count_words = self.tissue_description.split(', ')
        tissue_count = len(tissue_count_words)
        return tissue_count

    def get_sample_date_utc(self):
        sample_date_utc = datetime.datetime.strptime(self.sample_date_utc, '%Y-%m-%dT%H:%M:%SZ')
        return sample_date_utc

    def get_discrimination_factor(self, predator_delta13c: float):
        discrimination_factor = predator_delta13c - self.get_average_delta13c()
        return discrimination_factor

sample1 = PreySample(
full_species_name = 'Harbor Seal (Phoca vitulina)',
delta13c_list = [-12.4, -11.3, -10.6, -13.5, -15.8],
tissue_description = 'Bone collagen, Bone collagen, Muscle, Skin',
sample_date_utc = '2020-11-16T04:25:03Z',
)

print(sample1.get_common_name())
print(sample1.get_scientific_name())
print(sample1.get_average_delta13c())
print(sample1.get_tissue_count())
print(sample1.get_sample_date_utc())

sample2 = PreySample(
full_species_name = 'Pacific pomfret (Brama japonica)',
delta13c_list = [-16.1, -17.8, -19.6, -19.1, -18.0],
tissue_description = 'Whole animal',
sample_date_utc = '2020-11-17T05:00:02Z'
)

print(sample2.get_discrimination_factor(predator_delta13c=-15.5))