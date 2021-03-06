# Generated by Django 2.2 on 2019-09-25 17:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Atom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atomium_id', models.IntegerField()),
                ('name', models.CharField(max_length=32)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
                ('element', models.CharField(max_length=8)),
            ],
            options={
                'db_table': 'atoms',
            },
        ),
        migrations.CreateModel(
            name='Chain',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('atomium_id', models.CharField(max_length=128)),
                ('sequence', models.TextField()),
            ],
            options={
                'db_table': 'chains',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='ChainCluster',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'chain_clusters',
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('family', models.CharField(max_length=128)),
                ('keywords', models.CharField(max_length=1024)),
                ('classifications', models.CharField(max_length=1024)),
            ],
            options={
                'db_table': 'groups',
            },
        ),
        migrations.CreateModel(
            name='Pdb',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=1024)),
                ('classification', models.CharField(blank=True, max_length=1024, null=True)),
                ('keywords', models.CharField(blank=True, max_length=2048, null=True)),
                ('deposition_date', models.DateField(blank=True, null=True)),
                ('resolution', models.FloatField(blank=True, null=True)),
                ('rvalue', models.FloatField(blank=True, null=True)),
                ('organism', models.CharField(blank=True, max_length=1024, null=True)),
                ('expression_system', models.CharField(blank=True, max_length=1024, null=True)),
                ('technique', models.CharField(blank=True, max_length=1024, null=True)),
                ('assembly', models.IntegerField(blank=True, null=True)),
                ('skeleton', models.BooleanField()),
            ],
            options={
                'db_table': 'PDBs',
            },
        ),
        migrations.CreateModel(
            name='ZincSite',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('family', models.CharField(max_length=128)),
                ('residue_names', models.CharField(max_length=512)),
                ('representative', models.BooleanField(default=False)),
                ('group', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Group')),
                ('pdb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Pdb')),
            ],
            options={
                'db_table': 'zinc_sites',
            },
        ),
        migrations.CreateModel(
            name='StabilisingBond',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_atom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary_stabilisers', to='core.Atom')),
                ('secondary_atom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secondary_stabilisers', to='core.Atom')),
            ],
            options={
                'db_table': 'stabilising_bonds',
            },
        ),
        migrations.CreateModel(
            name='Residue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('residue_number', models.IntegerField()),
                ('insertion_code', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('atomium_id', models.CharField(max_length=128)),
                ('chain_identifier', models.CharField(max_length=128)),
                ('chain_signature', models.CharField(blank=True, max_length=128)),
                ('primary', models.BooleanField(default=True)),
                ('chain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Chain')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ZincSite')),
            ],
            options={
                'db_table': 'residues',
                'ordering': ['residue_number'],
            },
        ),
        migrations.CreateModel(
            name='Metal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atomium_id', models.IntegerField()),
                ('name', models.CharField(max_length=32)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
                ('element', models.CharField(max_length=8)),
                ('residue_name', models.CharField(max_length=32)),
                ('residue_number', models.IntegerField()),
                ('insertion_code', models.CharField(max_length=128)),
                ('chain_id', models.CharField(max_length=128)),
                ('omission_reason', models.TextField(blank=True, null=True)),
                ('pdb', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Pdb')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ZincSite')),
            ],
            options={
                'db_table': 'metals',
            },
        ),
        migrations.CreateModel(
            name='CoordinateBond',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Atom')),
                ('metal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Metal')),
            ],
            options={
                'db_table': 'coordinate_bonds',
            },
        ),
        migrations.CreateModel(
            name='ChainInteraction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequence', models.TextField()),
                ('chain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Chain')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ZincSite')),
            ],
            options={
                'db_table': 'chain_interactions',
            },
        ),
        migrations.AddField(
            model_name='chain',
            name='cluster',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.ChainCluster'),
        ),
        migrations.AddField(
            model_name='chain',
            name='pdb',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Pdb'),
        ),
        migrations.AddField(
            model_name='atom',
            name='residue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Residue'),
        ),
    ]
